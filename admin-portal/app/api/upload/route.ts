'User Server'

import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3"
import { getSignedUrl } from "@aws-sdk/s3-request-presigner"

type SignedURLResponse = Promise<
  { failure?: undefined; success: { url: string } }
  | { failure: string; success?: undefined }
>

const s3Client = new S3Client({
  region: process.env.NEXT_PUBLIC_AWS_BUCKET_REGION,
  credentials: {
    accessKeyId: process.env.NEXT_PUBLIC_AWS_ACCESS_KEY,
    secretAccessKey: process.env.NEXT_PUBLIC_AWS_SECRET_ACCESS_KEY,
  },
})

export async function getSignedURL(fileName: string): SignedURLResponse {
    const putObjectCommand = new PutObjectCommand({
      Bucket: process.env.NEXT_PUBLIC_AWS_BUCKET_NAME,
      Key: fileName,
    })

    const url = await getSignedUrl(
      s3Client,
      putObjectCommand,
      { expiresIn: 360 } // 360 seconds
    )

    return {success: {url}}
}