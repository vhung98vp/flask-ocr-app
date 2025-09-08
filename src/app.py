from flask import Flask, request, jsonify
import os
import tempfile
from werkzeug.utils import secure_filename
from kafka import start_kafka_consumer
from config import APP
from ocr.processor import process_file


app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Process uploaded file
    filename = secure_filename(file.filename)
    file_path = os.path.join(tempfile.gettempdir(), filename)
    try:
        file.save(file_path)
        result = process_file(file_path)
    except Exception as e:
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