# Multi-stage build for optimizing container image layer caching
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies (libgomp1 is required by FAISS CPU wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final production stage
FROM python:3.11-slim AS runner

WORKDIR /app

# Inject system library dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy installed libraries from builder stage
COPY --from=builder /root/.local /root/.local
COPY . .

# Environment paths configuration
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_ENV=production \
    PORT=8000 \
    HF_HOME=/root/.cache/huggingface

# Pre-create volume mount checkpoints
RUN mkdir -p logs data/vectorstore /root/.cache/huggingface

EXPOSE 8000

# Start server
CMD ["python", "main.py"]
