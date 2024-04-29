import boto3
import os
import uuid
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Key
from models import UserProfile, ChatSession, ChatMessage
from embeddings import EmbeddingProcessor

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# AWS Environment Variables
app.config['AWS_REGION'] = os.getenv('AWS_REGION')
app.config['AWS_S3_USER_IMAGE_BUCKET'] = os.getenv('AWS_S3_USER_IMAGE_BUCKET')
app.config['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID')
app.config['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY')
app.config['AWS_S3_SCD_DATA_BUCKET'] = os.getenv('AWS_S3_SCD_DATA_BUCKET')

# Amazon S3 Client Configuration
s3_client = boto3.client(
    's3',
    aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
    region_name=app.config['AWS_REGION']
)

# AWS DynamoDB Configuration
dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
        region_name=app.config['AWS_REGION']
    )

# AWS DynamoDB Tables
user_profile_table = dynamodb.Table('UserProfile')
chat_session_table = dynamodb.Table('ChatSession')
chat_message_table = dynamodb.Table('ChatMessage')

######################################################################
#  GET INDEX
######################################################################
@app.route('/')
def index():
    return render_template("index.html")

######################################################################
#  RECEIVE FILE UPLOAD NOTIFICATION AND CREATE EMBEDDINGS TO PINECONE
######################################################################
@app.route('/embeddings', methods=['POST'])
def create_embeddings():
    # Extract filename from the JSON payload sent by Lambda
    data = request.get_json()
    filename = data['filename']
    file_extension = filename.split('.')[-1].lower()  # Determine file extension for document type

    # Map extensions to document types used by EmbeddingProcessor
    doc_type = 'pdf' if file_extension == 'pdf' else 'txt'

    # Construct the full S3 object key if needed
    file_key = filename

    # Read the file content directly from S3
    try:
        response = s3_client.get_object(Bucket=app.config['AWS_S3_SCD_DATA_BUCKET'], Key=file_key)
        # Stream the file content. This handles both text and binary files.
        file_stream = response['Body']

        # Instantiate and process using the EmbeddingProcessor
        processor = EmbeddingProcessor(file_stream, doc_type)
        processor.process()

        return jsonify({"message": "Embeddings created and uploaded successfully.", "status": "success"}), 200

    except Exception as e:
        # Log the error or handle it appropriately
        return jsonify({"message": str(e), "status": "error"}), 500

######################################################################
#  START CHAT SESSION
######################################################################
@app.route('/chat/<string:user_id>/start_session', methods=['POST'])
def start_chat(user_id):
    # Generate a unique session ID
    session_id = str(uuid.uuid4())
    start_time = datetime.now(timezone.utc)

    # Create and save the new chat session
    chat_session = ChatSession(user_id, session_id, start_time)
    chat_session.save(chat_session_table)

    return jsonify({'session_id': session_id}), 200

######################################################################
#  HANDLE IN-PROGRESS CHAT SESSION
######################################################################
@app.route('/chat/<string:user_id>/<string:session_id>', methods=['POST'])
def chat(user_id, session_id):
    data = request.get_json()
    user_input = data.get('user_input', '')
    
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400

    user_input_timestamp = datetime.now(timezone.utc)
    response = simple_chatbot_logic(user_input)
    response_timestamp = datetime.now(timezone.utc)

    chat_message = ChatMessage(
        user_id, session_id, user_input, user_input_timestamp, response, response_timestamp
    )
    chat_message.save(chat_message_table)

    # Update the session's end_time to the latest activity time
    try:
        chat_session_table.update_item(
            Key={
                'user_id': user_id,
                'session_id': session_id
            },
            UpdateExpression='SET end_time = :val',
            ExpressionAttributeValues={
                ':val': response_timestamp.isoformat()
            },
            ReturnValues='UPDATED_NEW'
        )
    except Exception as e:
        return jsonify({'message': str(e), 'status': 'error'}), 500

    return jsonify({'response': response}), 200

######################################################################
#  RETRIEVE CHAT HISTORY
######################################################################
@app.route('/chat/<string:user_id>/history', methods=['GET'])
def get_chat_history(user_id):
    # Retrieve all sessions for the user
    session_response = chat_session_table.query(
        KeyConditionExpression=Key('user_id').eq(user_id)
    )
    # Convert sessions to list and sort by 'end_time' (handling None values as ongoing sessions)
    sessions = session_response['Items']
    sorted_sessions = sorted(
        sessions,
        key=lambda x: x.get('end_time', '9999-12-31T23:59:59'),  # Sort ongoing sessions as the most recent
        reverse=True  # Use reverse to sort from the most recently ended to the oldest
    )

    history = []
    for session in sorted_sessions:
        session_id = session['session_id']
        # Query for messages using the new composite sort key
        message_response = chat_message_table.query(
            KeyConditionExpression=Key('user_id').eq(user_id) & 
                                    Key('session_id_timestamp').begins_with(session_id),
            ScanIndexForward=True  # True for ascending order based on timestamp within the session_id
        )
        # Append messages along with session information
        history.append({
            'session_id': session_id,
            'start_time': session['start_time'],
            'end_time': session.get('end_time'),
            'messages': message_response['Items']
        })

    return jsonify({'history': history}), 200

######################################################################
#  GENERATE PRESIGNED URL FOR USER IMAGE UPLOAD
######################################################################
@app.route('/generate-presigned-url/<string:filename>', methods=['GET'])
def get_presigned_url(filename):
    if not filename:
        return jsonify({'error': 'Filename is required'}), 400

    url = create_presigned_url(app.config['AWS_S3_USER_IMAGE_BUCKET'], filename)
    if url:
        return jsonify({'url': url}), 200
    else:
        return jsonify({'error': 'Unable to generate pre-signed URL'}), 500

######################################################################
#  ADD USER PROFILE
######################################################################
@app.route('/profile', methods=['POST'])
def add_user_profile():
    data = request.get_json()
    image_name = data.get('image_name')

    # Construct the full S3 URL from the filename if image_name is provided
    if image_name:
        image_url = f"https://{app.config['AWS_S3_USER_IMAGE_BUCKET']}.s3.{app.config['AWS_REGION']}.amazonaws.com/{image_name}"
    else:
        image_url = None

    # Create an instance of UserProfile with the provided and constructed data
    user_profile = UserProfile(
        user_id=data.get('user_id'),
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        medical_id=data.get('medical_id'),
        preferred_name=data.get('preferred_name'),
        email=data.get('email'),
        user_image=image_url,
        expertise=data.get('expertise')
    )

    # Save the user profile to DynamoDB
    try:
        user_profile.save(user_profile_table)
        return jsonify({'message': 'User profile added successfully'}), 201
    except Exception as e:
        return jsonify({'message': str(e), 'status': 'error'}), 500

######################################################################
#  UPDATE EXISTING USER PROFILE
######################################################################
@app.route('/profile/<string:user_id>', methods=['PUT'])
def update_user_profile(user_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Prepare the update expression and attribute values
    update_expression = "set "
    expression_attribute_values = {}
    for key, value in data.items():
        if key == 'image_name':
            continue  # Skip image_name here, handle separately
        update_expression += f"{key} = :{key}, "
        expression_attribute_values[f":{key}"] = value

    # Special handling for image URL if image_name is provided
    if 'image_name' in data:
        image_url = f"https://{app.config['AWS_S3_USER_IMAGE_BUCKET']}.s3.{app.config['AWS_REGION']}.amazonaws.com/{data['image_name']}"
        update_expression += "user_image = :user_image, "
        expression_attribute_values[":user_image"] = image_url

    # Remove the trailing comma from the update expression
    if update_expression.endswith(", "):
        update_expression = update_expression[:-2]

    # Update the item in DynamoDB with a condition that the item must exist
    try:
        user_profile_table.update_item(
            Key={'user_id': user_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ConditionExpression="attribute_exists(user_id)",
            ReturnValues="UPDATED_NEW"
        )
        return jsonify({'message': 'User profile updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


######################################################################
#  RETRIEVE USER PROFILE
######################################################################
@app.route('/profile/<string:user_id>', methods=['GET'])
def get_user_profile(user_id):
    user_profile = UserProfile.get(user_id, user_profile_table)
    if not user_profile:
        return jsonify({'error': 'User not found'}), 404
    
    user_data = {
        'user_id': user_profile.user_id,
        'first_name': user_profile.first_name,
        'last_name': user_profile.last_name,
        'medical_id': user_profile.medical_id,
        'preferred_name': user_profile.preferred_name,
        'email': user_profile.email,
        'user_image': user_profile.user_image,
        'expertise': user_profile.expertise
    }
    return jsonify(user_data), 200

######################################################################
#  RETRIEVE FAQ
######################################################################
@app.route('/faq', methods=['GET'])
def get_faq():
    pass

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def simple_chatbot_logic(user_input):
    """
    A very simple chatbot logic that responds to user input.
    In the future, this could be replaced with more complex logic or AI.
    """
    if user_input.lower() == 'hello':
        return "Hello! How can I help you today?"
    elif user_input.lower() == 'bye':
        return "Goodbye! Have a great day!"
    elif user_input.lower() == 'thank you':
        return "You're welcome"
    elif user_input.lower() == 'what is scd?':
        return "Sickle cell disease (SCD) and its variants are genetic disorders resulting from the presence of a mutated form of hemoglobin, hemoglobin S (HbS). The most common form of SCD found in North America is homozygous HbS disease (HbSS), an autosomal recessive disorder first described by Herrick in 1910. SCD causes significant morbidity and mortality, particularly in people of African and Mediterranean ancestry. Morbidity, frequency of crisis, degree of anemia, and the organ systems involved vary considerably from individual to individual."
    else:
        return "I'm not sure how to respond to that. Can you try asking something else?"

def create_presigned_url(bucket_name, object_name, expiration=3600):
    try:
        response = s3_client.generate_presigned_url('put_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None

    return response


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
