FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    poppler-utils \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN pip install --no-cache-dir torch==2.8.0+cpu torchvision==0.23.0 torchaudio==2.8.0 \
    --index-url https://download.pytorch.org/whl/cpu
RUN python -c "from vietocr.tool.config import Cfg; from vietocr.tool.predictor import Predictor; config = Cfg.load_config_from_name('vgg_transformer'); predictor = Predictor(config)"
RUN python -c "from paddleocr import PaddleOCR; ocr = PaddleOCR(lang='en', use_angle_cls=True)"

COPY /src /app
WORKDIR /app

ENTRYPOINT ["python", "app.py"]