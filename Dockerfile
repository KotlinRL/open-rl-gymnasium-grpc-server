FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc swig \
    && apt-get clean && rm -rf /var/lib/apt/lists/*WORKDIR /home/appuser/app

RUN useradd --create-home appuser
RUN mkdir -p /home/appuser/app
RUN chown -R appuser:appuser /home/appuser

WORKDIR /home/appuser/app

COPY requirements.txt .
COPY src /home/appuser/app

RUN pip install --no-cache-dir -r requirements.txt

USER appuser

EXPOSE 50051

CMD ["python", "server.py"]