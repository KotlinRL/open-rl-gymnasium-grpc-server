# Use multi-stage builds
FROM python:3.13-slim AS builder

# Install build dependencies only in builder stage
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# Final stage
FROM python:3.13-slim

# Copy only the built wheels from builder
COPY --from=builder /wheels /wheels
COPY . .

RUN pip install --no-cache /wheels/*

# Add .dockerignore to exclude unnecessary fi   les