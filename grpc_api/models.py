import sqlalchemy
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

import os
from dotenv import load_dotenv, find_dotenv

# Pydantic models for normalization
from pydantic import BaseModel, Field
from typing import Optional

# Load environment variables from .env file
load_dotenv(find_dotenv())

DB_HOSTNAME = os.environ.get("DB_HOSTNAME", "localhost")
DB_NAME = os.environ.get("DB_NAME", "postgres")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
DB_PORT = os.environ.get("DB_PORT", 5432)

Base = declarative_base()

# --- SQLAlchemy Models ---

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True)
    run_id = Column(String, index=True)
    created_ts = Column(DateTime, default=datetime.utcnow)
    updated_ts = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    login = Column(String)
    node_id = Column(String)
    url = Column(String)
    repos_url = Column(String)
    events_url = Column(String)
    hooks_url = Column(String)
    issues_url = Column(String)
    members_url = Column(String)
    public_members_url = Column(String)
    avatar_url = Column(String)
    description = Column(String)
    is_verified = Column(Boolean)
    has_organization_projects = Column(Boolean)
    has_repository_projects = Column(Boolean)
    public_repos = Column(Integer)
    public_gists = Column(Integer)
    followers = Column(Integer)
    following = Column(Integer)

class Member(Base):
    __tablename__ = "members"
    id = Column(Integer, primary_key=True)
    run_id = Column(String, index=True)
    created_ts = Column(DateTime, default=datetime.utcnow)
    updated_ts = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    login = Column(String)
    node_id = Column(String)
    avatar_url = Column(String)
    gravatar_id = Column(String)
    url = Column(String)
    html_url = Column(String)
    followers_url = Column(String)
    following_url = Column(String)
    gists_url = Column(String)
    starred_url = Column(String)
    subscriptions_url = Column(String)
    organizations_url = Column(String)
    repos_url = Column(String)
    events_url = Column(String)
    received_events_url = Column(String)
    type = Column(String)
    user_view_type = Column(String)
    site_admin = Column(Boolean)
    mfa_enabled = Column(Boolean)

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    run_id = Column(String, index=True)
    created_ts = Column(DateTime, default=datetime.utcnow)
    updated_ts = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    name = Column(String)
    node_id = Column(String)
    slug = Column(String)
    description = Column(String)
    privacy = Column(String)
    notification_setting = Column(String)
    url = Column(String)
    html_url = Column(String)
    members_url = Column(String)
    repositories_url = Column(String)
    permission = Column(String)
    parent = Column(Integer)

class Repo(Base):
    __tablename__ = "repos"
    id = Column(Integer, primary_key=True)
    run_id = Column(String, index=True)
    created_ts = Column(DateTime, default=datetime.utcnow)
    updated_ts = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    node_id = Column(String)
    name = Column(String)
    full_name = Column(String)
    private = Column(Boolean)
    owner_login = Column(String)
    owner_id = Column(Integer)
    owner_node_id = Column(String)
    owner_avatar_url = Column(String)
    owner_gravatar_id = Column(String)
    owner_url = Column(String)
    owner_html_url = Column(String)
    owner_followers_url = Column(String)
    owner_following_url = Column(String)
    owner_gists_url = Column(String)
    owner_starred_url = Column(String)
    owner_subscriptions_url = Column(String)
    owner_organizations_url = Column(String)
    owner_repos_url = Column(String)
    owner_events_url = Column(String)
    owner_received_events_url = Column(String)
    owner_type = Column(String)
    owner_user_view_type = Column(String)
    owner_site_admin = Column(Boolean)
    html_url = Column(String)
    description = Column(String)
    fork = Column(Boolean)
    url = Column(String)
    forks_url = Column(String)
    created_at = Column(String)
    updated_at = Column(String)
    pushed_at = Column(String)
    archived = Column(Boolean)
    disabled = Column(Boolean)
    visibility = Column(String)
    allow_forking = Column(Boolean)
    web_commit_signoff_required = Column(Boolean)
    default_branch = Column(String)
    permissions = Column(JSON)
    security_and_analysis = Column(JSON)

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True)
    run_id = Column(String, index=True)
    created_ts = Column(DateTime, default=datetime.utcnow)
    updated_ts = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    repo_name = Column(String)
    login = Column(String)
    node_id = Column(String)
    avatar_url = Column(String)
    gravatar_id = Column(String)
    url = Column(String)
    html_url = Column(String)
    followers_url = Column(String)
    following_url = Column(String)
    gists_url = Column(String)
    starred_url = Column(String)
    subscriptions_url = Column(String)
    organizations_url = Column(String)
    repos_url = Column(String)
    events_url = Column(String)
    received_events_url = Column(String)
    type = Column(String)
    user_view_type = Column(String)
    site_admin = Column(Boolean)
    permissions = Column(JSON)
    role_name = Column(String)

# --- Pydantic Models for normalization ---

class OrganizationModel(BaseModel):
    run_id: str
    created_ts: datetime = Field(default_factory=datetime.utcnow)
    updated_ts: datetime = Field(default_factory=datetime.utcnow)
    id: int
    login: str
    node_id: Optional[str]
    url: Optional[str]
    repos_url: Optional[str]
    events_url: Optional[str]
    hooks_url: Optional[str]
    issues_url: Optional[str]
    members_url: Optional[str]
    public_members_url: Optional[str]
    avatar_url: Optional[str]
    description: Optional[str]
    is_verified: Optional[bool]
    has_organization_projects: Optional[bool]
    has_repository_projects: Optional[bool]
    public_repos: Optional[int]
    public_gists: Optional[int]
    followers: Optional[int]
    following: Optional[int]

class MemberModel(BaseModel):
    run_id: str
    created_ts: datetime = Field(default_factory=datetime.utcnow)
    updated_ts: datetime = Field(default_factory=datetime.utcnow)
    id: Optional[int]
    login: Optional[str]
    node_id: Optional[str]
    avatar_url: Optional[str]
    gravatar_id: Optional[str]
    url: Optional[str]
    html_url: Optional[str]
    followers_url: Optional[str]
    following_url: Optional[str]
    gists_url: Optional[str]
    starred_url: Optional[str]
    subscriptions_url: Optional[str]
    organizations_url: Optional[str]
    repos_url: Optional[str]
    events_url: Optional[str]
    received_events_url: Optional[str]
    type: Optional[str]
    user_view_type: Optional[str]
    site_admin: Optional[bool]
    mfa_enabled: Optional[bool] = None

class TeamModel(BaseModel):
    run_id: str
    created_ts: datetime = Field(default_factory=datetime.utcnow)
    updated_ts: datetime = Field(default_factory=datetime.utcnow)
    id: Optional[int]
    name: Optional[str]
    node_id: Optional[str]
    slug: Optional[str]
    description: Optional[str]
    privacy: Optional[str]
    notification_setting: Optional[str]
    url: Optional[str]
    html_url: Optional[str]
    members_url: Optional[str]
    repositories_url: Optional[str]
    permission: Optional[str]
    parent: Optional[int]

class RepoModel(BaseModel):
    run_id: str
    created_ts: datetime = Field(default_factory=datetime.utcnow)
    updated_ts: datetime = Field(default_factory=datetime.utcnow)
    id: Optional[int]
    node_id: Optional[str]
    name: Optional[str]
    full_name: Optional[str]
    private: Optional[bool]
    owner_login: Optional[str]
    owner_id: Optional[int]
    owner_node_id: Optional[str]
    owner_avatar_url: Optional[str]
    owner_gravatar_id: Optional[str]
    owner_url: Optional[str]
    owner_html_url: Optional[str]
    owner_followers_url: Optional[str]
    owner_following_url: Optional[str]
    owner_gists_url: Optional[str]
    owner_starred_url: Optional[str]
    owner_subscriptions_url: Optional[str]
    owner_organizations_url: Optional[str]
    owner_repos_url: Optional[str]
    owner_events_url: Optional[str]
    owner_received_events_url: Optional[str]
    owner_type: Optional[str]
    owner_user_view_type: Optional[str]
    owner_site_admin: Optional[bool]
    html_url: Optional[str]
    description: Optional[str]
    fork: Optional[bool]
    url: Optional[str]
    forks_url: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    pushed_at: Optional[str]
    archived: Optional[bool]
    disabled: Optional[bool]
    visibility: Optional[str]
    allow_forking: Optional[bool]
    web_commit_signoff_required: Optional[bool]
    default_branch: Optional[str]
    permissions: Optional[dict]
    security_and_analysis: Optional[dict]

class PermissionModel(BaseModel):
    run_id: str
    created_ts: datetime = Field(default_factory=datetime.utcnow)
    updated_ts: datetime = Field(default_factory=datetime.utcnow)
    repo_name: Optional[str]
    login: Optional[str]
    node_id: Optional[str]
    avatar_url: Optional[str]
    gravatar_id: Optional[str]
    url: Optional[str]
    html_url: Optional[str]
    followers_url: Optional[str]
    following_url: Optional[str]
    gists_url: Optional[str]
    starred_url: Optional[str]
    subscriptions_url: Optional[str]
    organizations_url: Optional[str]
    repos_url: Optional[str]
    events_url: Optional[str]
    received_events_url: Optional[str]
    type: Optional[str]
    user_view_type: Optional[str]
    site_admin: Optional[bool]
    permissions: Optional[dict]
    role_name: Optional[str]

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOSTNAME}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)