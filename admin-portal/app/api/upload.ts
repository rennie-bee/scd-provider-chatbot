// pages/api/upload.ts
import type { NextApiRequest, NextApiResponse } from 'next';
import AWS from 'aws-sdk';
import formidable, { Files, Fields } from 'formidable-serverless';
import fs from 'fs';

export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const form = new formidable.IncomingForm();

  form.parse(req, async (err: any, fields: Fields, files: Files) => {
    if (err) {
      return res.status(500).json({ error: "Error parsing the files" });
    }

    AWS.config.update({
      accessKeyId: process.env.AWS_ACCESS_KEY_ID,
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
      region: process.env.AWS_REGION,
    });

    const s3 = new AWS.S3();

    const file = Array.isArray(files.file) ? files.file[0] : files.file;

    try {
      const s3Response = await s3.upload({
        Bucket: process.env.AWS_S3_BUCKET as string,
        Key: `uploads/${file.originalFilename}`,
        Body: fs.createReadStream(file.filepath),
      }).promise();

      res.status(200).json({ message: "File uploaded successfully!", data: s3Response });
    } catch (error) {
      res.status(500).json({ error: "Error uploading to S3", details: error });
    }
  });
}