# rig-security-de

## Task Overview

Build a data pipeline and backend service that fetches repository metadata and access data from a GitHub organization, processes it into a normalized schema, stores it efficiently, and exposes gRPC endpoints to query this data. The system also allows policy-based querying or filtering (e.g., using OPA/CEL) to assess data quality or detect potential issues in access patterns.

---

## Solution Overview

Solution present with docker containers and docker compose for overall orchestration:
  - db
  - elt_service
  - grpc_api
  - opa_service

The ELT is implemented in a DAG-like way. Airflow, Temporal or luigi was not used to keep things simple.

### elt_service

Basic python container elt script. Written to represent a DAG with tasks.
Method: Datalake approach with data saved to disk (simulated bucket) between tasks.
There are 4 tasks:
1. Extract Raw data from Github.
2. Normalize data - used pydantic to validate data.
3. Check if destination table exist, else create them
4. Insert/Upsert data into table.

Typical Workflow:
Generate a new run_id (UUID4).
Extract raw data from GitHub and save to disk.
Normalize raw data to match database schema.
Ensure all tables exist in the database.
Load normalized data into the database.
Log all actions and handle errors gracefully.

### postgres_db

PostgresSQL 17 database to provide persistent storage and a target for the gRPC API.

### grpc_api

API to provide 3 enpoints as described in assessment.

### opa_service

Open Policy Agent implemented using container. Custom policies added via policy.rego.

## Sections Complete/Incomplete

1. ELT process - Done
2. Policy-based querying Rule Engine - OPA as service. NOT WORKING yet.
3. gRPC Backend - ELT Models for table schema.
  3.1 ListRepositories - Implemented with name filter and private/public repo.
  3.2 GetRepositoryAccessDetails - implemented with repository_name param
  3.3 EvaluatePolicy - Not working. Using OPA in container.

## Setup & Running (with Docker Compose)

### 1. Clone the repository

```bash
git clone https://github.com/grantav/rig-security-de.git
cd rig-security-de
```

### 2. Configure Environment Variables

Create a `.env` file in `elt_service/` with:

```
GH_PAT=your_github_pat
GH_ORG=your_github_org
DB_HOSTNAME=postgres_db
DB_NAME=rig-demo-01
DB_USER=rig-user01
DB_PASSWORD=rig-user01
DB_PORT=5432
```

Create a `.env` file in `grpc_api/` with:

```
DB_HOSTNAME=postgres_db
DB_NAME=rig-demo-01
DB_USER=rig-user01
DB_PASSWORD=rig-user01
DB_PORT=5432
```

### 3. Build All Images

```bash
docker-compose build
```

### 4. Run All Services

```bash
docker-compose up -d --force-recreate
```

This will start:
- `db`: PostgreSQL database.
- `elt_service`: Extracts, normalizes, and loads GitHub org data into the database.
- `grpc_api`: Exposes gRPC endpoints for querying the data.
- `opa_service`: Provide Open Policy Agent as independant service.

### 5. Stop All Services

In another terminal, run:

```bash
docker-compose down --remove-orphans
```

### 6. **Drop tables**

```sql
DROP TABLE public.members;
DROP TABLE public.organizations;
DROP TABLE public.permissions;
DROP TABLE public.repos;
DROP TABLE public.teams;
```

---

## Sample gRPC Requests

### grpcurl cli app

You can use [grpcurl](https://github.com/fullstorydev/grpcurl) or any gRPC client to interact with the API. The gRPC server runs on port `50051` by default.

#### Homebrew install grpcurl

```bash
brew install grpcurl
```

### Insomnia

GUI app with gRPC functionality. You can load the proto files created by running:

```bash
cd grpc_api/
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. elt_service.proto
```

#### Homebrew install Insomnia

```bash
brew install insomnia
```

### ListRepositories

```bash
grpcurl -plaintext -d '{"name_filter": "da", "private_only": true}' localhost:50051 eltservice.ELTService/ListRepositories
```

### GetRepositoryAccessDetails

```bash
grpcurl -plaintext -d '{"repository_name": "devops"}' localhost:50051 eltservice.ELTService/GetRepositoryAccessDetails
```

### EvaluatePolicy

```bash
grpcurl -plaintext -d '{"policy_name": "no_public_repos"}' localhost:50051 eltservice.ELTService/EvaluatePolicy
```

---

## Project Structure

- `elt_service/`: ELT pipeline (extract, normalize, load)
- `grpc_api/`: gRPC API server
- `docker-compose.yml`: Orchestrates all services
- `data/`: Raw and normalized data (for reference/debugging)

---

## Intended Use
- Security auditing of GitHub organizations
- Policy evaluation and reporting
- Tracking changes over time

---
