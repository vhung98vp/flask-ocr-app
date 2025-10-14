FROM nvidia/cuda:11.3.1-cudnn8-runtime-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive 

RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.9 python3.9-dev python3-distutils \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    poppler-utils \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3.9 get-pip.py

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip 1

# Install torch for CUDA 11.3
RUN pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 torchaudio==0.12.1 \
    --index-url https://download.pytorch.org/whl/cu113

# Download VietOCR models
RUN mkdir -p /root/.cache/torch/hub/checkpoints/
RUN curl -o /root/.cache/torch/hub/checkpoints/vgg19_bn-c79401a0.pth https://download.pytorch.org/models/vgg19_bn-c79401a0.pth

RUN pip install paddlepaddle-gpu==2.5.2

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

RUN apt-get update && apt-get install -y --no-install-recommends \
    libcudnn8=8.2.1.32-1+cuda11.3 \
    libcudnn8-dev=8.2.1.32-1+cuda11.3 \
 && rm -rf /var/lib/apt/lists/*

COPY /src/models /app/models/
COPY /src /app
WORKDIR /app

RUN mkdir -p /usr/local/lib64 && \
    if [ -f /usr/lib/x86_64-linux-gnu/libcudnn.so.8 ]; then \
        ln -sf /usr/lib/x86_64-linux-gnu/libcudnn.so.8 /usr/lib/x86_64-linux-gnu/libcudnn.so && \
        ln -sf /usr/lib/x86_64-linux-gnu/libcudnn.so.8 /usr/local/lib64/libcudnn.so; \
    elif [ -f /usr/local/cuda-11.3/targets/x86_64-linux-lib/libcudnn.so.8 ]; then \
        ln -sf /usr/local/cuda-11.3/targets/x86_64-linux-lib/libcudnn.so.8 /usr/local/lib64/libcudnn.so; \
    fi && \
    ldconfig

ENTRYPOINT ["python", "app.py"]