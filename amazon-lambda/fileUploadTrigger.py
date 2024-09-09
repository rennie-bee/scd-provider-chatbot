import boto3
import json

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Extract the bucket name and file key from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Get the file from S3
    response = s3.get_object(Bucket=bucket, Key=key)
    file_content = response['Body'].read()

    # Process the file content as needed
    # For example, if it's a text file, you can do:
    # content = file_content.decode('utf-8')

    return {
        'statusCode': 200,
        'body': json.dumps('File processed successfully!')
    }

