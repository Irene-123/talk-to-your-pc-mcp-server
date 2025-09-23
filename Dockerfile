# Dockerfile for Talk to Your PC MCP Server - Azure Deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for cross-platform support
RUN apt-get update && apt-get install -y \
    curl \
    net-tools \
    iputils-ping \
    procps \
    psmisc \
    wireless-tools \
    iproute2 \
    dnsutils \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional HTTP server dependencies
RUN pip install --no-cache-dir \
    fastapi>=0.100.0 \
    uvicorn[standard]>=0.23.0 \
    pydantic>=2.0.0 \
    psutil>=5.9.0


COPY *.py ./


RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser


EXPOSE 8081


HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8081/ || exit 1

# Set environment variables
ENV PORT=8081

# Run the HTTP server
CMD ["python", "http_server.py"]