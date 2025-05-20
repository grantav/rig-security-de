# gRPC Based API
# ListRepositories: List repositories with filtering options.
# GetRepositoryAccessDetails: Return user/team access for a repository.
# EvaluatePolicy: Run policy engine over the dataset and return violations.
# Add logging and basic metrics collection.

import grpc
from concurrent import futures
import logging
import json
from pathlib import Path
from elt_service_pb2 import (
    ListRepositoriesResponse, Repository,
    GetRepositoryAccessDetailsResponse, AccessDetail,
    EvaluatePolicyResponse, PolicyViolation
)
import elt_service_pb2_grpc
import grpc_reflection.v1alpha.reflection as grpc_reflection
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
sys.path.append(str(Path(__file__).parent.parent / "elt_service"))
from models import Base, Repo, Member, Team, Permission, Organization
import elt_service_pb2
import httpx

# Database connection (reuse .env from elt_service)
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

import os
DB_HOSTNAME = os.environ.get("DB_HOSTNAME", "localhost")
DB_NAME = os.environ.get("DB_NAME", "postgres")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
DB_PORT = os.environ.get("DB_PORT", 5432)
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOSTNAME}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

OPA_URL = os.environ.get("OPA_URL", "http://opa_service:8181/v1/data/rig/policies/deny")

class ELTServiceServicer(elt_service_pb2_grpc.ELTServiceServicer):
    def ListRepositories(self, request, context):
        session = SessionLocal()
        try:
            query = session.query(Repo)
            if request.name_filter:
                query = query.filter(Repo.name.contains(request.name_filter))
            if request.private_only:
                query = query.filter(Repo.private.is_(True))
            repos = query.all()
            filtered = [Repository(
                name=r.name or "",
                full_name=r.full_name or "",
                description=r.description or "",
                private=bool(r.private)
            ) for r in repos]
            logging.info(f"ListRepositories returned {len(filtered)} repositories (filter: '{request.name_filter}', private_only: {request.private_only})")
            return ListRepositoriesResponse(repositories=filtered)
        except Exception as e:
            logging.error(f"ListRepositories error: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return ListRepositoriesResponse()
        finally:
            session.close()

    def GetRepositoryAccessDetails(self, request, context):
        session = SessionLocal()
        try:
            repo = session.query(Repo).filter(Repo.name == request.repository_name).first()
            if not repo:
                context.set_details(f"Repository '{request.repository_name}' not found.")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return GetRepositoryAccessDetailsResponse()
            perms = session.query(Permission).filter(Permission.repo_name == request.repository_name).all()
            access = [AccessDetail(
                user_or_team=p.login or "unknown",
                type="user",  # Extend logic for teams if needed
                role=p.role_name or "unknown"
            ) for p in perms]
            logging.info(f"GetRepositoryAccessDetails for '{request.repository_name}' returned {len(access)} access records")
            return GetRepositoryAccessDetailsResponse(access=access)
        except Exception as e:
            logging.error(f"GetRepositoryAccessDetails error: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return GetRepositoryAccessDetailsResponse()
        finally:
            session.close()

    def EvaluatePolicy(self, request, context):
        session = SessionLocal()
        try:
            violations = []
            # For each user, repo, and permission, build input for OPA
            members = session.query(Member).all()
            repos = session.query(Repo).all()
            perms = session.query(Permission).all()
            # Build lookup for teams per user (if you have a team membership table, use it; else, skip teams)
            user_teams = {m.login: [] for m in members}
            # For each permission, evaluate OPA
            for p in perms:
                user = next((m for m in members if m.login == p.login), None)
                repo = next((r for r in repos if r.name == p.repo_name), None)
                if not user or not repo:
                    continue
                opa_input = {
                    "user": {
                        "login": user.login,
                        "mfa_enabled": getattr(user, "mfa_enabled", None),
                        "teams": user_teams.get(user.login, []),
                    },
                    "repo": {
                        "name": repo.name,
                    },
                    "permission": {
                        "level": p.role_name,
                    }
                }
                try:
                    resp = httpx.post(OPA_URL, json={"input": opa_input}, timeout=2)
                    resp.raise_for_status()
                    result = resp.json().get("result", [])
                    for reason in result:
                        violations.append(PolicyViolation(
                            entity=user.login or "",
                            violation=reason
                        ))
                except Exception as e:
                    logging.error(f"OPA evaluation error for user {user.login}, repo {repo.name}: {e}")
            logging.info(f"EvaluatePolicy OPA found {len(violations)} violations")
            return EvaluatePolicyResponse(violations=violations)
        except Exception as e:
            logging.error(f"EvaluatePolicy error: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return EvaluatePolicyResponse()
        finally:
            session.close()

async def serve():
    server = grpc.aio.server()
    elt_service_pb2_grpc.add_ELTServiceServicer_to_server(ELTServiceServicer(), server)
    SERVICE_NAMES = (
        elt_service_pb2.DESCRIPTOR.services_by_name['ELTService'].full_name,
        grpc_reflection.SERVICE_NAME,
    )
    grpc_reflection.enable_server_reflection(SERVICE_NAMES, server)
    server.add_insecure_port('[::]:50051')
    await server.start()
    logging.info("gRPC server started on port 50051 with reflection enabled")
    await server.wait_for_termination()

if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        logging.info("gRPC server stopped by KeyboardInterrupt...")
