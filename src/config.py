import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', 
                    handlers=[logging.StreamHandler(sys.stdout)]
                )

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger

APP = {
    'host': os.environ.get('APP_HOST', 'localhost'),
    'port': int(os.environ.get('APP_PORT', 5000)),
    'mode': os.environ.get('APP_MODE', 'api').lower()
}

KAFKA = {
    'brokers': os.environ.get('KAFKA_BOOTSTRAP_SERVER'),
    'consumer_group': os.environ.get('KAFKA_CONSUMER_GROUP', 'default'),
    'consumer_timeout': float(os.environ.get('KAFKA_CONSUMER_TIMEOUT', 1)),
    'auto_offset_reset': os.environ.get('KAFKA_AUTO_OFFSET_RESET', 'earliest'),
    'input_topic': os.environ.get('KAFKA_INPUT_TOPIC'),
    'output_topic': os.environ.get('KAFKA_OUTPUT_TOPIC'),
    'error_topic': os.environ.get('KAFKA_ERROR_TOPIC'),
    'complete_topic': os.environ.get('KAFKA_COMPLETE_TOPIC'),
    'doc_id_key': os.environ.get('KAFKA_DOC_ID_FIELD', '_fs_internal_id')
}

KAFKA_CONSUMER_CONFIG = {
    'bootstrap.servers': KAFKA['brokers'],
    'group.id': KAFKA['consumer_group'],
    'auto.offset.reset': KAFKA['auto_offset_reset']
}

KAFKA_PRODUCER_CONFIG = {
    'bootstrap.servers': KAFKA['brokers']
}

S3_READ_CONFIG = {
    'endpoint': os.environ.get('S3_READ_ENDPOINT'),
    'access_key': os.environ.get('S3_READ_ACCESS_KEY_ID'),
    'secret_key': os.environ.get('S3_READ_SECRET_ACCESS_KEY'),
    'bucket_name': os.environ.get('S3_READ_BUCKET_NAME')
}

S3_WRITE_CONFIG = {
    'endpoint': os.environ.get('S3_WRITE_ENDPOINT'),
    'access_key': os.environ.get('S3_WRITE_ACCESS_KEY_ID'),
    'secret_key': os.environ.get('S3_WRITE_SECRET_ACCESS_KEY'),
    'bucket_name': os.environ.get('S3_WRITE_BUCKET_NAME'),
    'upload_folder': os.environ.get('S3_WRITE_FOLDER', 'avatar')
}
