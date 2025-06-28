FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ swig libgl1-mesa-glx && \
    useradd --create-home appuser && \
    mkdir -p /home/appuser/app && \
    chown -R appuser:appuser /home/appuser


WORKDIR /home/appuser/app

COPY requirements.txt .
COPY src .
COPY protos /protos

RUN pip install --upgrade pip setuptools wheel && \
    pip install --prefer-binary --no-cache-dir -r requirements.txt && \
    apt-get remove -y gcc g++ swig && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* && \
    pip cache purge


RUN python -m grpc_tools.protoc \
    -I/protos \
    --python_out=/home/appuser/app \
    --grpc_python_out=/home/appuser/app \
    /protos/*.proto

RUN rm -rf /protos requirements.txt

USER appuser

EXPOSE 50051

CMD ["python", "server.py"]