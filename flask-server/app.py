import boto3
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from models import db, UserProfile
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config.from_pyfile('settings.py')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/mydatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['AWS_S3_BUCKET'] = 'your-s3-bucket-name'
app.config['AWS_REGION'] = 'your-region'
app.config['AWS_ACCESS_KEY'] = 'your-access-key-id'
app.config['AWS_SECRET_ACCESS_KEY'] = 'your-secret-access-key'
db.init_app(app)

s3_client = boto3.client(
    's3',
    aws_access_key_id=app.config['AWS_ACCESS_KEY'],
    aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
    region_name=app.config['AWS_REGION']
)

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
    data = request.json
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
#  ADD USER PROFILE
######################################################################
@app.route('/profile', methods=['POST'])
def add_user_profile():
    data = request.form
    file = request.files['user_image']
    filename = secure_filename(file.filename)
    image_url = upload_file_to_s3(file, app.config['AWS_S3_BUCKET'], filename)

    user = UserProfile(
        user_id=data['user_id'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        medical_id=data.get('medical_id'),
        preferred_name=data.get('preferred_name'),
        email=data['email'],
        user_image=image_url,  # URL from S3
        expertise=data.get('expertise')
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

    data = request.form
    image_file = request.files.get('user_image')
    if image_file:
        filename = secure_filename(image_file.filename)
        image_url = upload_file_to_s3(image_file, app.config['AWS_S3_BUCKET'], filename)
        user.user_image = image_url

    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.medical_id = data.get('medical_id', user.medical_id)
    user.preferred_name = data.get('preferred_name', user.preferred_name)
    user.email = data.get('email', user.email)
    user.expertise = data.get('expertise', user.expertise)
    
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

def upload_file_to_s3(file, bucket_name, object_name=None):
    """ Upload a file to an S3 bucket """
    if object_name is None:
        object_name = file.filename

    try:
        response = s3_client.upload_fileobj(
            file,
            bucket_name,
            object_name,
            ExtraArgs={'ACL': 'public-read'}
        )
        return f"https://{bucket_name}.s3.{app.config['AWS_REGION']}.amazonaws.com/{secure_filename(object_name)}"
    except Exception as e:
        print(f"Something went wrong: {e}")
        return None


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
