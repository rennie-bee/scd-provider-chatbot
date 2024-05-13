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
from chatbotLLM import HeadAgent

# Load environment variables from .env file
load_dotenv()

application = Flask(__name__)
CORS(application)

# Pinecone and OpenAI configuration
application.config['PINECONE_API_KEY'] = os.getenv('PINECONE_API_KEY')
application.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
application.config['PINECONE_INDEX_NAME'] = os.getenv('PINECONE_INDEX_NAME')

# AWS Environment Variables
application.config['AWS_REGION'] = os.getenv('AWS_REGION')
application.config['AWS_S3_USER_IMAGE_BUCKET'] = os.getenv('AWS_S3_USER_IMAGE_BUCKET')
application.config['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID')
application.config['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY')
application.config['AWS_S3_SCD_DATA_BUCKET'] = os.getenv('AWS_S3_SCD_DATA_BUCKET')

# Amazon S3 Client Configuration
s3_client = boto3.client(
    's3',
    aws_access_key_id=application.config['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=application.config['AWS_SECRET_ACCESS_KEY'],
    region_name=application.config['AWS_REGION']
)

# AWS DynamoDB Configuration
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=application.config['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=application.config['AWS_SECRET_ACCESS_KEY'],
    region_name=application.config['AWS_REGION']
)

# AWS DynamoDB Tables
user_profile_table = dynamodb.Table('UserProfile')
chat_session_table = dynamodb.Table('ChatSession')
chat_message_table = dynamodb.Table('ChatMessage')

######################################################################
#  GET INDEX
######################################################################
@application.route('/')
def index():
    return render_template("index.html")

######################################################################
#  RECEIVE FILE UPLOAD NOTIFICATION AND CREATE EMBEDDINGS TO PINECONE
######################################################################
@application.route('/embeddings', methods=['POST'])
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
        response = s3_client.get_object(Bucket=application.config['AWS_S3_SCD_DATA_BUCKET'], Key=file_key)
        # Stream the file content. This handles both text and binary files.
        file_stream = response['Body']

        # Instantiate and process using the EmbeddingProcessor
        processor = EmbeddingProcessor(
            file_stream=file_stream, 
            doc_type=doc_type,
            api_key=application.config['PINECONE_API_KEY'],
            openai_key=application.config['OPENAI_API_KEY'],
            index_name=application.config['PINECONE_INDEX_NAME']
        )
        processor.process()

        return jsonify({"message": "Embeddings created and uploaded successfully.", "status": "success"}), 200

    except Exception as e:
        # Log the error or handle it appropriately
        return jsonify({"message": str(e), "status": "error"}), 500

######################################################################
#  START CHAT SESSION
######################################################################
@application.route('/chat/<string:user_id>/start_session', methods=['POST'])
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
@application.route('/chat/<string:user_id>/<string:session_id>', methods=['POST'])
def chat(user_id, session_id):
    data = request.get_json()
    user_input = data.get('user_input')
    message_id = data.get('message_id')
    user_input_timestamp = data.get('timestamp')
    
    if not user_input:
        return jsonify({'error': 'No user input provided'}), 400
    if not message_id:
        return jsonify({'error': 'No message id provided'}), 400

    # user_input_timestamp = datetime.now(timezone.utc)
    # Retrieve previous chat messages
    history = []
    history.append(('assistant', 'What would you like to chat about?'))
    # Construct the session_id to use in querying messages
    user_session_id = f"{user_id}#{session_id}"
    # Query for messages using the composite message_id key
    try:
        message_response = chat_message_table.query(
            KeyConditionExpression=Key('user_session_id').eq(user_session_id),
            ScanIndexForward=True  # True for ascending order of the sort key
        )
    except Exception as e:
        return jsonify({'message': str(e), 'status': 'error'}), 500

    messages = message_response['Items']
    for message in messages:
        history.append(('user', message['user_input']))
        history.append(('assistant', message['chatbot_response']))

    # Initialize head agent of LLM model
    head_agent = HeadAgent(
        openai_key=application.config['OPENAI_API_KEY'], 
        pinecone_key=application.config['PINECONE_API_KEY'], 
        pinecone_index_name=application.config['PINECONE_INDEX_NAME'],
        messages=history
    )
    # Set up chat mode, e.g. chatty
    head_agent.setup_sub_agents()

    # Get response from the LLM model
    chatbot_response = head_agent.process_input(user_input)
    chatbot_response_timestamp = user_input_timestamp
    # message_id = uuid() # Generate a unique message ID 
    timestamp = datetime.now(timezone.utc)

    chat_message = ChatMessage(
        user_id=user_id, 
        session_id=session_id, 
        message_id=message_id,
        timestamp=timestamp, 
        user_input=user_input, 
        user_input_timestamp=user_input_timestamp, 
        chatbot_response=chatbot_response, 
        chatbot_response_timestamp=chatbot_response_timestamp
    )

    # Save chat message
    try:
        chat_message.save(chat_message_table)
    except Exception as e:
        return jsonify({'message': str(e), 'status': 'error'}), 500

    # Update the session's end_time to the latest activity time
    try:
        chat_session_table.update_item(
            Key={
                'user_id': user_id,
                'session_id': session_id
            },
            UpdateExpression='SET end_time = :val',
            ExpressionAttributeValues={
                ':val': timestamp.isoformat()
            },
            ReturnValues='UPDATED_NEW'
        )
    except Exception as e:
        return jsonify({'message': str(e), 'status': 'error'}), 500

    return jsonify({'message_id': message_id, 'response': chatbot_response}), 200

######################################################################
#  UPDATE CHATBOT RESPONSE TIMESTAMP
######################################################################
@application.route('/chat/<string:user_id>/<string:session_id>/<string:message_id>/timestamp', methods=['PUT'])
def update_chatbot_response_timestamp(user_id, session_id, message_id):
    data = request.get_json()
    
    chatbot_response_timestamp = data.get('timestamp')
    if not chatbot_response_timestamp:
        return jsonify({'error': 'Missing timestamp'}), 400

    # Use the GSI to get the primary key values
    try:
        response = chat_message_table.query(
            IndexName='user_session_id-message_id-index',
            KeyConditionExpression='user_session_id = :usi AND message_id = :mi',
            ExpressionAttributeValues={
                ':usi': f"{user_id}#{session_id}",
                ':mi': message_id
            }
        )
        items = response['Items']
        if not items:
            return jsonify({'error': 'No item found with the given ID'}), 404
        
        primary_key = items[0]['user_session_id']  # Replace 'PrimaryKey' with the name of your table's primary key attribute
        sort_key = items[0]['timestamp']
        # Update the item in the main table
        chat_message_table.update_item(
            Key={
                'user_session_id': primary_key,
                'timestamp': sort_key
            },
            UpdateExpression='SET chatbot_response_timestamp = :val',
            ExpressionAttributeValues={
                ':val': chatbot_response_timestamp
            },
            ReturnValues="UPDATED_NEW"
        )
        return jsonify({'message': 'Chatbot response timestamp updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

######################################################################
#  REGENERATE CHATBOT RESPONSE
######################################################################
@application.route('/chat/<string:user_id>/<string:session_id>/<string:message_id>/regenerate', methods=['POST'])
def regenerate_answer(user_id, session_id, message_id):
    data = request.get_json()
    user_input = data.get('user_input')
    
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400
    
    user_input_timestamp = datetime.now(timezone.utc)
    # Construct the session_id to use in deleting and querying messages
    user_session_id = f"{user_id}#{session_id}"
    # Delete chat message with the same id
    try:
        chat_message_table.delete_item(
            Key={
                'user_session_id': user_session_id,
                'message_id': message_id # Use GSI to delete message
            }
        )
    except Exception as e:
        return jsonify({'message': str(e), 'status': 'error'}), 500

    # Retrieve previous chat messages
    history = []
    history.append(('assistant', 'What would you like to chat about?'))

    # Query for messages using the composite message_id key
    try:
        message_response = chat_message_table.query(
            KeyConditionExpression=Key('user_session_id').eq(user_session_id),
            ScanIndexForward=True  # True for ascending order of the sort key
        )
    except Exception as e:
        return jsonify({'message': str(e), 'status': 'error'}), 500

    messages = message_response['Items']
    for message in messages:
        history.append(('user', message['user_input']))
        history.append(('assistant', message['chatbot_response']))

    # Initialize head agent of LLM model
    head_agent = HeadAgent(
        openai_key=application.config['OPENAI_API_KEY'], 
        pinecone_key=application.config['PINECONE_API_KEY'], 
        pinecone_index_name=application.config['PINECONE_INDEX_NAME'],
        messages=history
    )
    # Set up chat mode, e.g. chatty
    head_agent.setup_sub_agents()

    # Get response from the LLM model
    chatbot_response = head_agent.process_input(user_input)
    chatbot_response_timestamp = datetime.now(timezone.utc)
    message_id = str(uuid.uuid4()) # Generate a unique message ID 
    timestamp = datetime.now(timezone.utc)

    chat_message = ChatMessage(
        user_id=user_id, 
        session_id=session_id, 
        message_id=message_id,
        timestamp=timestamp, 
        user_input=user_input, 
        user_input_timestamp=user_input_timestamp, 
        chatbot_response=chatbot_response, 
        chatbot_response_timestamp=chatbot_response_timestamp
    )

    # Save chat message
    try:
        chat_message.save(chat_message_table)
    except Exception as e:
        return jsonify({'message': str(e), 'status': 'error'}), 500

    # Update the session's end_time to the latest activity time
    try:
        chat_session_table.update_item(
            Key={
                'user_id': user_id,
                'session_id': session_id
            },
            UpdateExpression='SET end_time = :val',
            ExpressionAttributeValues={
                ':val': timestamp.isoformat()
            },
            ReturnValues='UPDATED_NEW'
        )
    except Exception as e:
        return jsonify({'message': str(e), 'status': 'error'}), 500

    return jsonify({'response': chatbot_response}), 200

######################################################################
#  RETRIEVE CHAT HISTORY
######################################################################
@application.route('/chat/<string:user_id>/history', methods=['GET'])
def get_chat_history(user_id):
    # Retrieve all sessions for the user
    try:
        session_response = chat_session_table.query(
            KeyConditionExpression=Key('user_id').eq(user_id)
        )
    except Exception as e:
        return jsonify({'message': str(e), 'status': 'error'}), 500
    
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
        # Construct the session_id to use in querying messages
        user_session_id = f"{user_id}#{session_id}"
        # Query for messages using the composite message_id key
        try:
            message_response = chat_message_table.query(
                KeyConditionExpression=Key('user_session_id').eq(user_session_id),
                ScanIndexForward=True  # True for ascending order of the sort key
            )
        except Exception as e:
            return jsonify({'message': str(e), 'status': 'error'}), 500
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
@application.route('/generate-presigned-url/<string:filename>', methods=['GET'])
def get_presigned_url(filename):
    if not filename:
        return jsonify({'error': 'Filename is required'}), 400

    url = create_presigned_url(application.config['AWS_S3_USER_IMAGE_BUCKET'], filename)
    if url:
        return jsonify({'url': url}), 200
    else:
        return jsonify({'error': 'Unable to generate pre-signed URL'}), 500

######################################################################
#  ADD USER PROFILE
######################################################################
@application.route('/profile', methods=['POST'])
def add_user_profile():
    data = request.get_json()
    image_name = data.get('image_name')

    # Construct the full S3 URL from the filename if image_name is provided
    if image_name:
        image_url = f"https://{application.config['AWS_S3_USER_IMAGE_BUCKET']}.s3.{application.config['AWS_REGION']}.amazonaws.com/{image_name}"
    else:
        image_url = None

    # Create an instance of UserProfile with the provided and constructed data
    user_profile = UserProfile(
        user_id=data.get('user_id'),
        user_name=data.get('user_name'),
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
@application.route('/profile/<string:user_id>', methods=['PUT'])
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
        image_url = f"https://{application.config['AWS_S3_USER_IMAGE_BUCKET']}.s3.{application.config['AWS_REGION']}.amazonaws.com/{data['image_name']}"
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
@application.route('/profile/<string:user_id>', methods=['GET'])
def get_user_profile(user_id):
    user_profile = UserProfile.get(user_id, user_profile_table)
    if not user_profile:
        return jsonify({'error': 'User not found'}), 404
    
    user_data = {
        'user_id': user_profile.user_id,
        'user_name': user_profile.user_name,
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
@application.route('/faq', methods=['GET'])
def get_faq():
    pass

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
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
    application.run(port=8080, debug=True)
