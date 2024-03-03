import json

def lambda_handler(event, context):
    # Print the event to see the structure
    print("Received event: " + json.dumps(event, indent=2))

    # Extract bucket name
    bucket = event['Records'][0]['s3']['bucket']['name']
    # Extract file name
    key = event['Records'][0]['s3']['object']['key']
    
    print(f"File uploaded: {key} in bucket: {bucket}")

    # Add your processing logic here

    return {
        'statusCode': 200,
        'body': json.dumps('File processed successfully!')
    }
