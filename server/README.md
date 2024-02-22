## Set up Flask on your local machine

To set up Flask, please follow these steps:

1. Ensure you have installed the latest version of [Python](https://www.python.org/downloads/)

2. Clone the repository:
```bash
git clone https://github.com/rennie-bee/scd-provider-chatbot.git
```

3. Navigate to the server directory:
```bash
cd scd-provider-chatbot
cd server
```

4. Install the required packages:
```bash
pip install -r requirements.txt
```
This will install all the Python packages needed for the Flask application as listed in `requirements.txt`.

## Running Flask
After installing, you can start the Flask application using:
```bash
python -m flask run
```
Open http://localhost:5000 with your browser to see the Flask page.