import os
import boto3
from botocore.client import Config
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from config import S3_CONFIG


class S3Client:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            endpoint_url=S3_CONFIG['endpoint'],
            aws_access_key_id=S3_CONFIG['access_key'],
            aws_secret_access_key=S3_CONFIG['secret_key'],
            config=Config(signature_version='s3v4', s3={'addressing_style': 'path'}),
            verify=False
        )

    def is_file_exists(self, file_key, bucket_name=S3_CONFIG['bucket_name']):
        try:
            self.s3.head_object(Bucket=bucket_name, Key=file_key)
            return True
        except Exception:
            return False

    def list_files(self, prefix, bucket_name=S3_CONFIG['bucket_name']):
        try:
            response = self.s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
        except (NoCredentialsError, PartialCredentialsError) as e:
            raise Exception("AWS credentials not found or incomplete.") from e
        except Exception as e:
            raise Exception("Error listing files in S3 bucket.") from e

    def download_file(self, file_key, bucket_name=S3_CONFIG['bucket_name']):
        try:
            download_path = "/tmp/" + file_key.split('/')[-1]
            with open(download_path, 'wb') as f:
                self.s3.download_fileobj(bucket_name, file_key, f)
            return download_path
        except Exception as e:
            raise Exception(f"Error downloading file {file_key} from S3.") from e
    
    def upload_file(self, local_path, file_key, folder=S3_CONFIG['upload_folder'], bucket_name=S3_CONFIG['bucket_name']):
        try:
            upload_key = os.path.join(folder, file_key)
            with open(local_path, 'rb') as f:
                self.s3.upload_fileobj(f, bucket_name, upload_key)
            return f"s3://{bucket_name}/{file_key}"
        except Exception as e:
            raise Exception(f"Error uploading file to {file_key} in S3.") from e