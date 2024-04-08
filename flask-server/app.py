from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

# Start user's chat
@app.route('/chat/<str:username>/start_session', methods=['POST'])
def start_chat(username):
    pass

# Handle in-progress user's chat
@app.route('/chat/<str:username>/<int:session_id>', methods=['POST'])
def chat(username, session_id):
    data = request.json
    user_input = data.get('user_input', '')
    
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400

    response = simple_chatbot_logic(user_input)
    return jsonify({'response': response})

# End user's chat
@app.route('/chat/<str:username>/<int:session_id>/end_session', methods=['POST'])
def end_chat(username, session_id):
    pass


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

# Retrieve user's chat history
@app.route('/chat/<str:username>/history', methods=['GET'])
def get_chat_history(username):
    pass

# Add user's profile
@app.route('/profile', methods=['POST'])
def add_user_profile():
    pass

# Update user's profile
@app.route('/profile/<str:username>', methods=['PUT'])
def update_user_profile(username):
    pass

# Retrieve user's profile
@app.route('/profile/<str:username>', methods=['GET'])
def get_user_profile(username):
    pass

# FAQ
@app.route('/faq', methods=['GET'])
def get_faq():
    pass

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
