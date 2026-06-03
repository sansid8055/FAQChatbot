FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for torch and sentence-transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories (will be ephemeral unless mounted as volume)
RUN mkdir -p data/chroma data/threads data/logs

# Railway sets PORT dynamically; backend must bind to 0.0.0.0
ENV API_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

EXPOSE 8765

# Entrypoint: runs ingest on first deploy if ChromaDB is missing, then starts API
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
