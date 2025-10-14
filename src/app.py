from flask import Flask, request, jsonify
import os
import tempfile
from werkzeug.utils import secure_filename
from kafka import start_kafka_consumer
from config import APP, get_logger
from ocr.processor import process_file
logger = get_logger(__name__)


app = Flask(__name__)
app.json.ensure_ascii = False

@app.route('/manage/health', methods=['GET'])
def manage_health():
    return jsonify({"status": True}), 200


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    detect_type = request.args.get('type', '2')
    if detect_type not in ['0', '1', '2']:
        return jsonify({"error": "Invalid type. Must be 0, 1, or 2."}), 400
    
    # Process uploaded file
    filename = secure_filename(file.filename)
    file_path = os.path.join(tempfile.gettempdir(), filename)
    
    try:
        logger.info(f"Process type {detect_type}. Uploading file to {file_path}...")
        file.save(file_path)
        result = process_file(file_path, int(detect_type))
    except Exception as e:
        logger.exception(f"Error processing file {file_path}: {e}")
        return jsonify({'error': str(e)}), 500
    finally: # Clean file
        if os.path.exists(file_path):
            os.remove(file_path)

    # Return result
    return jsonify(result), 200

if __name__ == '__main__':
    if APP['mode'] == 'api':
        app.run(host=APP['host'], port=APP['port'])
    else:
        start_kafka_consumer()