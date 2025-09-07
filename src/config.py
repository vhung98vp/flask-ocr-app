import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(threadName)s - %(message)s'
)
logger = logging.getLogger(__name__)

APP = {
    'host': os.environ.get('APP_HOST', '0.0.0.0'),
    'port': int(os.environ.get('APP_PORT', 5001))
}

KAFKA = {
    'brokers': os.environ.get('KAFKA_BOOTSTRAP_SERVER'),
    'consumer_group': os.environ.get('KAFKA_CONSUMER_GROUP', 'default_consumer_group'),
    'consumer_timeout': float(os.environ.get('KAFKA_CONSUMER_TIMEOUT', 1)),
    'auto_offset_reset': os.environ.get('KAFKA_AUTO_OFFSET_RESET', 'earliest'),
    'input_topic': os.environ.get('KAFKA_INPUT_TOPIC'),
    'output_topic': os.environ.get('KAFKA_OUTPUT_TOPIC'),
    'error_topic': os.environ.get('KAFKA_ERROR_TOPIC')
}

KAFKA_CONSUMER_CONFIG = {
    'bootstrap.servers': KAFKA['brokers'],
    'group.id': KAFKA['consumer_group'],
    'auto.offset.reset': KAFKA['auto_offset_reset']
}

KAFKA_PRODUCER_CONFIG = {
    'bootstrap.servers': KAFKA['brokers']
}

S3_CONFIG = {
    'endpoint': os.environ.get('S3_ENDPOINT'),
    'access_key': os.environ.get('S3_ACCESS_KEY_ID'),
    'secret_key': os.environ.get('S3_SECRET_ACCESS_KEY'),
    'bucket_name': os.environ.get('S3_BUCKET_NAME'),
    'upload_folder': os.environ.get('S3_UPLOAD_FOLDER', 'avatar')
}

VIETOCR_CONFIG = {
    'base_config': os.environ.get('VIETOCR_BASE_CONFIG_PATH'),
    'transformer_config': os.environ.get('VIETOCR_TRANSFORMER_CONFIG_PATH'),
    'model_weight': os.environ.get('VIETOCR_MODEL_WEIGHT_PATH'),
    'device': os.environ.get('VIETOCR_DEVICE', 'cpu')
}

PADDLE_CONFIG = {
    'language': os.environ.get('PADDLEOCR_LANGUAGE', 'en'),
    'det_model_dir': os.environ.get('PADDLEOCR_DET_MODEL_DIR'),
    'rec_model_dir': os.environ.get('PADDLEOCR_REC_MODEL_DIR'),
    'cls_model_dir': os.environ.get('PADDLEOCR_CLS_MODEL_DIR')
}
