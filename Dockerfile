FROM nvidia/cuda:12.9.1-cudnn-runtime-ubuntu22.04


ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONUNBUFFERED=1


RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.12 python3.12-dev python3.12-distutils python3-pip \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    poppler-utils \
    git && \
    rm -rf /var/lib/apt/lists/*
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN pip install --no-cache-dir torch==2.8.0 torchvision==0.23.0 torchaudio==2.8.0 \
    --index-url https://download.pytorch.org/whl/cpu

# Download VietOCR models
RUN python -c "from vietocr.tool.config import Cfg; from vietocr.tool.predictor import Predictor; config = Cfg.load_config_from_name('vgg_transformer'); predictor = Predictor(config)"

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