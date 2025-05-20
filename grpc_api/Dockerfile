# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy proto and server code
COPY elt_service.proto .
# Generate Python code from proto file
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. elt_service.proto
# Copy server code
COPY server.py .
COPY models.py .

# Expose gRPC port
EXPOSE 50051

# Start gRPC server
# CMD ["python", "server.py"]
# Start gRPC server with specific port and threads
CMD ["python", "server.py", "--port=50051", "--threads=10"]

