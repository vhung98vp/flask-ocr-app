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
RUN pip install --no-cache-dir torch==2.8.0+cpu torchvision==0.23.0+cpu torchaudio==2.8.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# Download VietOCR models
RUN python -c "from vietocr.tool.config import Cfg; from vietocr.tool.predictor import Predictor; config = Cfg.load_config_from_name('vgg_transformer'); config['device'] = 'cpu'; predictor = Predictor(config)"

# Download PaddleOCR models
RUN mkdir -p /root/.paddleocr/whl/det/en/en_PP-OCRv3_det_infer && \
    python -c "from paddleocr import paddleocr; \
paddleocr.download_with_progressbar('https://paddleocr.bj.bcebos.com/PP-OCRv3/english/en_PP-OCRv3_det_infer.tar', \
'/root/.paddleocr/whl/det/en/en_PP-OCRv3_det_infer/en_PP-OCRv3_det_infer.tar')"
RUN mkdir -p /root/.paddleocr/whl/rec/en/en_PP-OCRv4_rec_infer && \
    python -c "from paddleocr import paddleocr; \
paddleocr.download_with_progressbar('https://paddleocr.bj.bcebos.com/PP-OCRv4/english/en_PP-OCRv4_rec_infer.tar', \
'/root/.paddleocr/whl/rec/en/en_PP-OCRv4_rec_infer/en_PP-OCRv4_rec_infer.tar')"
RUN mkdir -p /root/.paddleocr/whl/cls/ch_ppocr_mobile_v2.0_cls_infer && \
    python -c "from paddleocr import paddleocr; \
paddleocr.download_with_progressbar('https://paddleocr.bj.bcebos.com/dygraph_v2.0/ch/ch_ppocr_mobile_v2.0_cls_infer.tar', \
'/root/.paddleocr/whl/cls/ch_ppocr_mobile_v2.0_cls_infer/ch_ppocr_mobile_v2.0_cls_infer.tar')"

COPY vgg_transformer.pth /app/models/vietocr/
COPY /src /app
WORKDIR /app

ENTRYPOINT ["python", "app.py"]