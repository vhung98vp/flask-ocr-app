import os
import boto3
from botocore.client import Config
from botocore.exceptions import NoCredentialsError, PartialCredentialsError


class S3Client:
    def __init__(self, conf):
        self.s3 = boto3.client(
            's3',
            endpoint_url=conf.get('endpoint'),
            aws_access_key_id=conf.get('access_key'),
            aws_secret_access_key=conf.get('secret_key'),
            config=Config(signature_version='s3v4', s3={"addressing_style": "path"}),
            verify=False
        )
        self.bucket_name = conf.get('bucket_name')
        self.upload_folder = conf.get('upload_folder')

    def is_file_exists(self, file_key):
        try:
            self.s3.head_object(Bucket=self.bucket_name, Key=file_key)
            return True
        except Exception:
            return False

    def list_files(self, prefix):
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
        except (NoCredentialsError, PartialCredentialsError) as e:
            raise Exception(f"AWS credentials not found or incomplete: {e}")
        except Exception as e:
            raise Exception(f"Error listing files in S3 bucket: {e}")

    def download_file(self, file_key):
        try:
            download_path = "/tmp/" + file_key.split('/')[-1]
            with open(download_path, 'wb') as f:
                self.s3.download_fileobj(self.bucket_name, file_key, f)
            return download_path
        except Exception as e:
            raise Exception(f"Error downloading file {file_key} from S3: {e}")

    def upload_file(self, local_path, file_key):
        try:
            upload_key = os.path.join(self.upload_folder, file_key)
            self.s3.upload_file(local_path, self.bucket_name, upload_key)
            return f"s3://{self.bucket_name}/{upload_key}"
            # with open(local_path, 'rb') as f:
            #     self.s3.upload_fileobj(f, self.bucket_name, upload_key)
            # return f"s3://{self.bucket_name}/{upload_key}"
        except Exception as e:
            raise Exception(f"Error uploading file to {upload_key} in S3: {e}")