'User Server'

import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3"
import { getSignedUrl } from "@aws-sdk/s3-request-presigner"

type SignedURLResponse = Promise<
  { failure?: undefined; success: { url: string } }
  | { failure: string; success?: undefined }
>

const s3Client = new S3Client({
  region: "us-west-1",
  credentials: {
    accessKeyId: "AKIAYS2NRN2N2K6R2BFB",
    secretAccessKey: "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",
  },
})

export async function getSignedURL(): SignedURLResponse {
    const putObjectCommand = new PutObjectCommand({
      Bucket: "uw-scd-data",
      Key: "test-file",
    })

    const url = await getSignedUrl(
      s3Client,
      putObjectCommand,
      { expiresIn: 360 } // 360 seconds
    )

    return {success: {url}}
}