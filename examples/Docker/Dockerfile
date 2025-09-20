FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for cross-platform support
RUN apt-get update && apt-get install -y \
    curl \
    net-tools \
    iputils-ping \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY setup.py .
COPY README.md .

# Install the package
RUN pip install -e .

# Set environment variables
ENV PYTHONPATH=/app/src

# Run the MCP server
CMD ["talk-to-your-pc-mcp-server"]