# gRPC API Service

This service exposes a gRPC API for querying normalized GitHub organization data stored in a PostgreSQL database. It provides endpoints for listing repositories, retrieving repository access details, and evaluating policy violations.

## Features
- **ListRepositories**: List repositories with optional filtering (by name, privacy).
- **GetRepositoryAccessDetails**: Return user/team access for a repository.
- **EvaluatePolicy**: Run policy engine over the dataset and return violations (e.g., public repo detection).
- **Server Reflection**: Enabled for easy client development and testing.

## Requirements
- Python 3.11+
- PostgreSQL database (populated by the ELT pipeline)
- Docker (recommended)

## Build & Run (Docker)

Reccomend using docker compose build for images.

1. **Build the Docker image:**

```bash
cd grpc_api
docker build -t grpc_api .
```

2. **Run with Docker Compose (recommended):**

From the project root:

```bash
docker-compose up --build grpc_api
```

This will start the database, ELT service, and gRPC API together.

3. **Run standalone (for development):**

Advise that a virtual env be created or use a Conda env.

Install requirements, then build protobuff, then start the server.

```bash
pip install -r requirements.txt
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. elt_service.proto
python server.py
```

## Proto & Code Generation
- The proto file (`elt_service.proto`) is compiled at build time in the Dockerfile.
- Generated files: `elt_service_pb2.py`, `elt_service_pb2_grpc.py`.

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. elt_service.proto
```

## API Endpoints
- gRPC server listens on port `50051`.
- Reflection is enabled for easy client discovery.

## Example Usage
- Use any gRPC client (e.g., `grpcurl`, `Insomnia`) to call the API.
- See `elt_service.proto` for message and service definitions.

---
