FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc g++ swig \
        libgl1 \
        libglx0 \
        libxext6 libxrender1 libsm6 \
        xvfb x11-xserver-utils \
    && useradd --create-home appuser \
    && mkdir -p /home/appuser/app \
    && chown -R appuser:appuser /home/appuser


WORKDIR /home/appuser/app

COPY requirements.txt .
COPY src .
COPY protos /protos

RUN pip install --upgrade pip setuptools wheel && \
    pip install --prefer-binary --no-cache-dir -r requirements.txt && \
    apt-get remove -y gcc g++ swig && \
    apt-get autoremove -y && \
    python -m grpc_tools.protoc \
        -I/protos \
        --python_out=/home/appuser/app \
        --grpc_python_out=/home/appuser/app \
        /protos/*.proto && \
    pip cache purge && \
    rm -rf /var/lib/apt/lists/* /root/.cache /root/.local /tmp/* && \
    rm -rf /protos requirements.txt

USER appuser

EXPOSE 50051

CMD /bin/sh -c "rm -f /tmp/.X1-lock && Xvfb :1 -screen 0 1024x768x24 & export DISPLAY=:1 && python server.py"
