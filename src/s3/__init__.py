from .client import S3Client
from config import S3_READ_CONFIG, S3_WRITE_CONFIG

RClient = S3Client(S3_READ_CONFIG)
WClient = S3Client(S3_WRITE_CONFIG)
