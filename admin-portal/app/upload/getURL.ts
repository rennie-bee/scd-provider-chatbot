'User Server'

import { S3Client, PutObjectCommand, S3ClientConfig } from "@aws-sdk/client-s3"
import { getSignedUrl } from "@aws-sdk/s3-request-presigner"

// This type represents the possible responses of the getSignedURL function
type SignedURLResponse = Promise<
  { failure?: undefined; success: { url: string } } // Success response with the URL
  | { failure: string; success?: undefined } // Failure response with an error message
>

// List of allowed file types for upload
const allowedFileTypes = [
  "text/plain", // .txt files
  "application/pdf", // .pdf files
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document", // .docx files
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" // .xlsx files
]

const maxFileSize = 1048576 * 1000 // Maximum file size limit (100 MB)

// Environment variables for AWS configuration
const awsRegion = process.env.NEXT_PUBLIC_AWS_BUCKET_REGION; // AWS region
const awsAccessKeyId = process.env.NEXT_PUBLIC_AWS_ACCESS_KEY; // AWS access key ID
const awsSecretAccessKey = process.env.NEXT_PUBLIC_AWS_SECRET_ACCESS_KEY; // AWS secret access key
const awsBucketName = process.env.NEXT_PUBLIC_AWS_BUCKET_NAME; // AWS S3 bucket name

// Validation to ensure AWS configuration is set
if (!awsRegion || !awsAccessKeyId || !awsSecretAccessKey) {
  throw new Error("AWS configuration is not properly set in environment variables");
}

// S3 client configuration
const s3Config: S3ClientConfig = {
  region: awsRegion,
  credentials: {
    accessKeyId: awsAccessKeyId,
    secretAccessKey: awsSecretAccessKey,
  },
}

// Creating an instance of S3Client with the above configuration
const s3Client = new S3Client(s3Config);

// Async function to get a pre-signed URL for file upload
export async function getSignedURL(file: File): SignedURLResponse {
    // Checking if the file type is allowed
    if(!allowedFileTypes.includes(file.type)) {
      return {failure: "File type not allowed"}
    }

    // Checking if the file size is within the limit
    if(file.size > maxFileSize) {
      return {failure: "File size too large"}
    }

    // Creating a PutObjectCommand for the file to be uploaded
    const putObjectCommand = new PutObjectCommand({
      Bucket: awsBucketName, // S3 bucket name
      Key: file.name, // The name/key of the file in the S3 bucket
    })

    // Generating a pre-signed URL for the putObjectCommand
    const url = await getSignedUrl(
      s3Client,
      putObjectCommand,
      { expiresIn: 360 } // URL expiry time in seconds (360 seconds = 6 minutes)
    )
    
    // Returning the success response with the URL
    return {success: {url}}
}