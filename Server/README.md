## Set up Flask on your local machine

To set up Flask, follow these steps:

1. Ensure you have installed the latest version of [Python](https://www.python.org/downloads/)

2. Clone the repository:
```shell 
$git clone https://github.com/rennie-bee/scd-provider-chatbot.git
```

3. Navigate to the Server directory:
```shell
$cd scd-provider-chatbot
$cd Server
```

4. Install the required packages:
```shell
$pip install -r requirements.txt
```
This will install all the Python packages needed for the Server as listed in `requirements.txt`.

## Running Flask
After installing, you can start the Flask application using:
```shell
$python -m flask run
```