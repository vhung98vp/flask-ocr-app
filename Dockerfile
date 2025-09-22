FROM nvidia/cuda:11.3.1-runtime-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive 

RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.10 python3.10-dev \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    poppler-utils \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3.10 get-pip.py

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip 1

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Install torch for CUDA 11.3
RUN pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 torchaudio==0.12.1 \
    --index-url https://download.pytorch.org/whl/cu113

# Download VietOCR models
RUN python -c "from vietocr.tool.config import Cfg; from vietocr.tool.predictor import Predictor; config = Cfg.load_config_from_name('vgg_transformer');"

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