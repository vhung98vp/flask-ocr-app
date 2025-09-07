# Flask OCR App

This project is a Flask-based API service designed to process files using Optical Character Recognition (OCR). It listens for messages from a Kafka topic containing S3 folder paths, processes PDF and image files, and returns the results in JSON format. The service also supports direct HTTP requests for file uploads.

## Project Structure

```
flask-ocr-app
├── src
│   ├── app.py                # Entry point of the Flask application
│   ├── ocr
│   │   ├── model.py          # OCR Model for processing
│   │   ├── pattern.py        # Patterns for ids extraction
│   │   ├── processor.py      # Logic for processing OCR on files
│   │   └── utils.py          # Utility functions for OCR processing
│   ├── s3
│   │   ├── __init__.py       # Init class for S3
│   │   └── client.py         # Class for interacting with AWS S3
│   ├── kafka.py              # Kafka processing logic
│   ├── config.py             # Configuration settings from environment variables
│   └── models                # Models pre-trained for OCR
├── requirements.txt           # Project dependencies
├── Dockerfile                 # Instructions for building the Docker image
├── .env.example               # Example environment variables
├── README.md                  # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone https://github.com/vhung98vp/flask-ocr-app
   cd flask-ocr-app
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Copy `.env.example` to `.env` in `src` and replace in the required values for S3 and Kafka configurations.

5. **Build the Docker image:**
   ```
   docker build -t flask-ocr-app .
   ```

6. **Run the application:**
   ```
   python src/app.py
   ```

## Usage

### API Endpoints

- **POST /upload**
  - Upload a PDF or image file for OCR processing.
  - Request Body: Form-data with the file.
  - Response: JSON containing the file path, file name, title, data inside, and detected IDs.

### Kafka Integration

- The service listens for messages on a Kafka topic containing S3 folder paths. Upon receiving a message, it lists the files in the specified S3 bucket, processes them for OCR, and sends the results to a new Kafka topic.

## License

This project is licensed under the MIT License. See the LICENSE file for details.