from flask import Flask, request, jsonify

app = Flask(__name__)

def simple_chatbot_logic(user_input):
    """
    A very simple chatbot logic that responds to user input.
    In a real application, this could be replaced with more complex logic or AI.
    """
    if user_input.lower() == 'hello':
        return "Hello! How can I help you today?"
    elif user_input.lower() == 'bye':
        return "Goodbye! Have a great day!"
    else:
        return "I'm not sure how to respond to that. Can you try asking something else?"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '')
    
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400

    response = simple_chatbot_logic(user_input)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
