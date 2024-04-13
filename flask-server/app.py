import boto3
import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from models import db, UserProfile
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['AWS_REGION'] = os.getenv('AWS_REGION')
app.config['AWS_S3_BUCKET'] = os.getenv('AWS_S3_BUCKET')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

s3_client = boto3.client(
    's3',
    aws_access_key_id=app.config['AWS_ACCESS_KEY'],
    aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
    region_name=app.config['AWS_REGION']
)

db.init_app(app)

######################################################################
#  GET INDEX
######################################################################
@app.route('/')
def index():
    return render_template("index.html")

######################################################################
#  START CHAT SESSION
######################################################################
@app.route('/chat/<string:user_id>/start_session', methods=['POST'])
def start_chat(user_id):
    pass

######################################################################
#  HANDLE IN-PROGRESS CHAT SESSION
######################################################################
@app.route('/chat/<string:user_id>/<int:session_id>', methods=['POST'])
def chat(user_id, session_id):
    data = request.get_json()
    user_input = data.get('user_input', '')
    
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400

    response = simple_chatbot_logic(user_input)
    return jsonify({'response': response})

######################################################################
#  END CHAT SESSION
######################################################################
@app.route('/chat/<string:user_id>/<int:session_id>/end_session', methods=['POST'])
def end_chat(user_id, session_id):
    pass

######################################################################
#  RETRIEVE CHAT HISTORY
######################################################################
@app.route('/chat/<string:user_id>/history', methods=['GET'])
def get_chat_history(user_id):
    pass

######################################################################
#  GENERATE PRESIGNED URL FOR USER IMAGE UPLOAD AND RETRIEVE
######################################################################
@app.route('/generate-presigned-url/<string:filename>', methods=['GET'])
def get_presigned_url(filename):
    if not filename:
        return jsonify({'error': 'Filename is required'}), 400

    url = create_presigned_url(app.config['AWS_S3_BUCKET'], filename)
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
    user_id = data.get('user_id')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    medical_id = data.get('medical_id')
    preferred_name = data.get('preferred name')
    email = data.get('email')
    filename = data.get('filename')
    expertise = data.get('expertise')

    if filename:
        # Construct the full S3 URL from the filename
        image_url = f"https://{app.config['AWS_S3_BUCKET']}.s3.{app.config['AWS_REGION']}.amazonaws.com/{filename}"
    else:
        image_url = None

    user = UserProfile(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        medical_id=medical_id,
        preferred_name=preferred_name,
        email=email,
        user_image=image_url,
        expertise=expertise
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User profile added successfully'}), 201

######################################################################
#  UPDATE EXISTING USER PROFILE
######################################################################
@app.route('/profile/<string:user_id>', methods=['PUT'])
def update_user_profile(user_id):
    user = UserProfile.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}, 400)

    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.medical_id = data.get('medical_id', user.medical_id)
    user.preferred_name = data.get('preferred_name', user.preferred_name)
    user.email = data.get('email', user.email)
    user.expertise = data.get('expertise', user.expertise)

    # Check if a new image filename is provided to update the image URL
    if 'filename' in data:
        user.user_image = f"https://{app.config['AWS_S3_BUCKET']}.s3.{app.config['AWS_REGION']}.amazonaws.com/{data.get('filename')}"
    
    db.session.commit()
    return jsonify({'message': 'User profile updated'}), 200

######################################################################
#  RETRIEVE USER PROFILE
######################################################################
@app.route('/profile/<string:user_id>', methods=['GET'])
def get_user_profile(user_id):
    user = UserProfile.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user_data = {
        'user_id': user.user_id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'medical_id': user.medical_id,
        'preferred_name': user.preferred_name,
        'email': user.email,
        'user_image': user.user_image,
        'expertise': user.expertise
    }
    return jsonify(user_data)

######################################################################
#  Retrieve FAQ
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
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None

    return response


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
