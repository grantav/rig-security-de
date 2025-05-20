# ELT Service

## Overview

This Python service extracts, normalizes, and loads GitHub organization data into a PostgreSQL database for security auditing and policy analysis.

- Extracts organization, repository, team, member, and permission data from the GitHub API.
- Normalizes and transforms the data into structured entities (e.g., Repositories, Users, Teams, Permissions) using Pydantic models.
- Stores the data in a persistent layer (PostgreSQL) using SQLAlchemy ORM.
- Supports tracking of data over time using run_id and timestamps.
- Includes robust logging and error handling.

## Features
- Extraction: Fetches all relevant org data from GitHub and saves as raw JSON.
- Normalization: Validates and transforms raw data to match the database schema.
- Loading: Inserts normalized data into the database with upsert logic.
- Table Management: Ensures all tables exist before loading.
- Logging: All steps are logged for traceability.

## Requirements
- Python 3.11+
- PostgreSQL database
- GitHub Personal Access Token (with org/repo read permissions)

## Setup & Build Instructions

1. **Clone the repository**

```bash
git clone <your-repo-url>
cd elt_service
```

2. **Set up environment variables**

Create a `.env` file in the project root with:

```
GH_PAT=your_github_pat
GH_ORG=your_github_org
DB_HOSTNAME=your_db_host
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_PORT=5432
```

3. **Build and run with Docker**

Reccomend using docker compose build for images.

```bash
docker build -t elt_service .
docker run --env-file .env elt_service
```

Or use Docker Compose (recommended for local dev):

```bash
docker-compose up --build
```

4. **Run locally (for development)**

```bash
pip install -r requirements.txt
python app.py
```

5. **Drop tables**

```sql
DROP TABLE public.members;
DROP TABLE public.organizations;
DROP TABLE public.permissions;
DROP TABLE public.repos;
DROP TABLE public.teams;
```

## Output
- Raw and normalized data are saved under `data/raw/{run_id}/` and `data/normalized/{run_id}/`.
- Data is loaded into the configured PostgreSQL database.

## Intended Use
- Security auditing of GitHub organizations
- Policy evaluation and reporting
- Tracking changes over time

---