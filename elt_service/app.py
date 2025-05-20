import os
import json
import logging
from uuid import uuid4
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
import httpx
from datetime import datetime, timezone

from models import OrganizationModel, MemberModel, TeamModel, RepoModel, PermissionModel
from models import SessionLocal, Base, engine
from sqlalchemy.exc import IntegrityError

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv(find_dotenv())

GH_PAT = os.getenv("GH_PAT")
GH_ORG = os.getenv("GH_ORG")

headers = {
    "Authorization": f"Bearer {GH_PAT}",
    "Accept": "application/vnd.github+json"
}

def list_repos():
    url = f"https://api.github.com/orgs/{GH_ORG}/repos"
    try:
        response = httpx.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch repos: {e}")
        return []

def list_teams():
    url = f"https://api.github.com/orgs/{GH_ORG}/teams"
    try:
        response = httpx.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch teams: {e}")
        return []

def list_members():
    url = f"https://api.github.com/orgs/{GH_ORG}/members"
    try:
        response = httpx.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch members: {e}")
        return []

def get_permissions(repo_name):
    url = f"https://api.github.com/repos/{GH_ORG}/{repo_name}/collaborators"
    try:
        response = httpx.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch permissions for repo {repo_name}: {e}")
        return []

def get_org_details():
    url = f"https://api.github.com/orgs/{GH_ORG}"
    try:
        response = httpx.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch org details: {e}")
        return {}

def ensure_tables_exist():
    """Create all tables in the database if they do not exist."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Ensured all tables exist in the database.")
    except Exception as e:
        logger.error(f"Error ensuring tables exist: {e}")
        raise

def extract_and_write_raw(run_id):
    """Extract data from GitHub and write to data/raw/{run_id}/ as JSON."""
    raw_dir = Path(f"data/raw/{run_id}")
    raw_dir.mkdir(parents=True, exist_ok=True)

    try:
        repos = list_repos()
        repo_names = [repo.get("name") for repo in repos if repo.get("name")]
        teams = list_teams()
        members = list_members()
        permissions = {repo: get_permissions(repo) for repo in repo_names}
        org_details = get_org_details()

        with open(raw_dir / "repos.json", "w") as f:
            json.dump(repos, f, indent=4)
        with open(raw_dir / "teams.json", "w") as f:
            json.dump(teams, f, indent=4)
        with open(raw_dir / "members.json", "w") as f:
            json.dump(members, f, indent=4)
        with open(raw_dir / "permissions.json", "w") as f:
            json.dump(permissions, f, indent=4)
        with open(raw_dir / "org_details.json", "w") as f:
            json.dump(org_details, f, indent=4)

        logger.info(f"Extracted raw data to {raw_dir}")
    except Exception as e:
        logger.error(f"Error during extraction: {e}")
        raise

def normalize_raw_data(run_id):
    """Normalize raw data using Pydantic models and write to data/normalized/{run_id}/ as JSON."""
    raw_dir = Path(f"data/raw/{run_id}")
    norm_dir = Path(f"data/normalized/{run_id}")
    norm_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)

    try:
        # --- Organization ---
        with open(raw_dir / "org_details.json") as f:
            org = json.load(f)
        org_obj = OrganizationModel(run_id=run_id, created_ts=now, updated_ts=now, **org)
        with open(norm_dir / "organizations.json", "w") as f:
            json.dump([org_obj.model_dump()], f, indent=4, default=str)

        # --- Members ---
        with open(raw_dir / "members.json") as f:
            members = json.load(f)
        member_objs = []
        for m in members:
            if "mfa_enabled" not in m:
                m["mfa_enabled"] = None
            try:
                member_objs.append(MemberModel(run_id=run_id, created_ts=now, updated_ts=now, **m).model_dump())
            except Exception as e:
                logger.warning(f"Skipping member due to error: {e}")
        with open(norm_dir / "members.json", "w") as f:
            json.dump(member_objs, f, indent=4, default=str)

        # --- Teams ---
        with open(raw_dir / "teams.json") as f:
            teams = json.load(f)
        team_objs = []
        for t in teams:
            try:
                team_objs.append(TeamModel(run_id=run_id, created_ts=now, updated_ts=now, **t).model_dump())
            except Exception as e:
                logger.warning(f"Skipping team due to error: {e}")
        with open(norm_dir / "teams.json", "w") as f:
            json.dump(team_objs, f, indent=4, default=str)

        # --- Repos ---
        with open(raw_dir / "repos.json") as f:
            repos = json.load(f)
        repo_objs = []
        for r in repos:
            owner = r.get("owner", {})
            repo_flat = {
                **r,
                "owner_login": owner.get("login"),
                "owner_id": owner.get("id"),
                "owner_node_id": owner.get("node_id"),
                "owner_avatar_url": owner.get("avatar_url"),
                "owner_gravatar_id": owner.get("gravatar_id"),
                "owner_url": owner.get("url"),
                "owner_html_url": owner.get("html_url"),
                "owner_followers_url": owner.get("followers_url"),
                "owner_following_url": owner.get("following_url"),
                "owner_gists_url": owner.get("gists_url"),
                "owner_starred_url": owner.get("starred_url"),
                "owner_subscriptions_url": owner.get("subscriptions_url"),
                "owner_organizations_url": owner.get("organizations_url"),
                "owner_repos_url": owner.get("repos_url"),
                "owner_events_url": owner.get("events_url"),
                "owner_received_events_url": owner.get("received_events_url"),
                "owner_type": owner.get("type"),
                "owner_user_view_type": owner.get("user_view_type"),
                "owner_site_admin": owner.get("site_admin"),
            }
            try:
                repo_objs.append(RepoModel(run_id=run_id, created_ts=now, updated_ts=now, **repo_flat).model_dump())
            except Exception as e:
                logger.warning(f"Skipping repo due to error: {e}")
        with open(norm_dir / "repos.json", "w") as f:
            json.dump(repo_objs, f, indent=4, default=str)

        # --- Permissions ---
        with open(raw_dir / "permissions.json") as f:
            permissions = json.load(f)
        perm_objs = []
        for repo_name, perms in permissions.items():
            for perm in perms:
                perm_data = {"repo_name": repo_name, **perm}
                try:
                    perm_objs.append(PermissionModel(run_id=run_id, created_ts=now, updated_ts=now, **perm_data).model_dump())
                except Exception as e:
                    logger.warning(f"Skipping permission due to error: {e}")
        with open(norm_dir / "permissions.json", "w") as f:
            json.dump(perm_objs, f, indent=4, default=str)

        logger.info(f"Normalized data written to {norm_dir}")
    except Exception as e:
        logger.error(f"Error during normalization: {e}")
        raise

def load_normalized_to_db(run_id):
    """
    Load normalized data from data/normalized/{run_id}/ into the database tables.
    
    The load_normalized_to_db function uses session.merge(obj) for each record.
    In SQLAlchemy, session.merge() performs an upsert: it inserts the record if it does not exist,
    or updates the existing record if it matches the primary key.
    Therefore, load_normalized_to_db performs an upsert (insert or update) for each record.
    """

    norm_dir = Path(f"data/normalized/{run_id}")
    session = SessionLocal()
    try:
        # --- Organization (single record) ---
        with open(norm_dir / "organizations.json") as f:
            orgs = json.load(f)
        for org in orgs:
            from models import Organization
            obj = Organization(**org)
            session.merge(obj)

        # --- Members ---
        with open(norm_dir / "members.json") as f:
            members = json.load(f)
        for m in members:
            from models import Member
            obj = Member(**m)
            session.merge(obj)

        # --- Teams ---
        with open(norm_dir / "teams.json") as f:
            teams = json.load(f)
        for t in teams:
            from models import Team
            obj = Team(**t)
            session.merge(obj)

        # --- Repos ---
        with open(norm_dir / "repos.json") as f:
            repos = json.load(f)
        for r in repos:
            from models import Repo
            obj = Repo(**r)
            session.merge(obj)

        # --- Permissions ---
        with open(norm_dir / "permissions.json") as f:
            perms = json.load(f)
        for p in perms:
            from models import Permission
            obj = Permission(**p)
            session.merge(obj)

        session.commit()
        logger.info("Loaded normalized data into the database.")
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Database integrity error: {e}")
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {e}")
    finally:
        session.close()
        
if __name__ == "__main__":
    run_id = str(uuid4())
    try:
        extract_and_write_raw(run_id)
        normalize_raw_data(run_id)
        ensure_tables_exist()
        load_normalized_to_db(run_id)
        logger.info("ELT process completed successfully.")
    except Exception as e:
        logger.error(f"ELT process failed: {e}")


# --- Notes ---
"""
This project implements a robust ELT (Extract, Load, Transform) pipeline for ingesting, normalizing, and storing GitHub organization security data into a PostgreSQL database. The pipeline is written in Python and uses SQLAlchemy for ORM, Pydantic for data validation, and httpx for API calls. Logging and error handling are integrated throughout.

Key Features:

Extraction:
Fetches organization details, repositories, teams, members, and repository permissions from the GitHub API using a personal access token. Raw JSON files are saved under data/raw/{run_id}/.

Normalization:
Raw JSON is loaded and normalized using Pydantic models that mirror the SQLAlchemy database schema. Normalized data is written as JSON to data/normalized/{run_id}/. Each record includes metadata fields: run_id, created_ts, and updated_ts.

Database Schema:
SQLAlchemy models define tables for organizations, members, teams, repositories, and permissions, including all relevant security-related fields and metadata.

Table Management:
The pipeline checks for and creates database tables as needed before loading data.

Loading:
Normalized data is loaded into the PostgreSQL database using SQLAlchemy ORM, with upsert (merge) logic and transaction management.

Logging & Error Handling:
All steps include detailed logging and robust error handling to ensure traceability and reliability.

Configuration:
Environment variables (via .env) are used for database and GitHub credentials. The project is containerized with Docker and supports orchestration with Docker Compose.

Typical Workflow:

Generate a new run_id (UUID4).
Extract raw data from GitHub and save to disk.
Normalize raw data to match database schema.
Ensure all tables exist in the database.
Load normalized data into the database.
Log all actions and handle errors gracefully.
"""