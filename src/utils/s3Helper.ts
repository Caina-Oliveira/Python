import AWS from 'aws-sdk';

export async function uploadToS3(
  accessKey: string,
  secretAccessKey: string,
  bucketName: string,
  key: string,
  file: string | Buffer | Uint8Array | Blob,
): Promise<void> {
  AWS.config.credentials = new AWS.Credentials({
    accessKeyId: accessKey,
    secretAccessKey,
  });

  const { S3 } = AWS;

  const s3 = new S3({ region: 'us-west-2' });

  await s3
    .upload({
      Key: key,
      Bucket: bucketName,
      Body: file,
    })
    .promise();
}
