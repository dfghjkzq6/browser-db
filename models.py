#!/usr/bin/env python3
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SameSiteEnum(str, Enum):
    STRICT = "Strict"
    LAX = "Lax"
    NONE = "None"
    NULL = "None"

class CookieModel(BaseModel):
    name: str = Field(..., description="Cookie name")
    value: str = Field(default="", description="Cookie value")
    domain: str = Field(..., description="Domain for the cookie")
    path: str = Field(default="/", description="Path for the cookie")
    expires: int = Field(default=-1, description="Expiration timestamp")
    httpOnly: bool = Field(default=False, description="HTTP only flag")
    secure: bool = Field(default=True, description="Secure flag")
    sameSite: Optional[SameSiteEnum] = Field(default=None, description="SameSite attribute")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class StorageStateModel(BaseModel):
    cookies: List[CookieModel] = Field(default_factory=list, description="List of cookies")
    origins: List[Dict[str, Any]] = Field(default_factory=list, description="List of origins")

class StorageStateInfo(BaseModel):
    timestamp: str = Field(..., description="Timestamp of the storage state")
    source: str = Field(..., description="Source of the storage state")
    cookies_count: int = Field(..., description="Number of cookies")
    file: str = Field(..., description="File path")

class DatabaseMetadata(BaseModel):
    created: str = Field(..., description="Creation timestamp")
    version: str = Field(default="1.0.0", description="Database version")
    description: str = Field(..., description="Database description")
    updated: Optional[str] = Field(None, description="Last update timestamp")

class SessionMetadata(BaseModel):
    name: str = Field(..., description="Session name")
    description: str = Field(default="", description="Session description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class SessionModel(BaseModel):
    id: str = Field(..., description="Session ID")
    created: str = Field(..., description="Creation timestamp")
    name: str = Field(..., description="Session name")
    description: str = Field(default="", description="Session description")
    storage_snapshot: StorageStateModel = Field(..., description="Storage state snapshot")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class DatabaseModel(BaseModel):
    metadata: DatabaseMetadata = Field(..., description="Database metadata")
    storage_states: Dict[str, StorageStateInfo] = Field(default_factory=dict, description="Storage states")
    sessions: List[SessionModel] = Field(default_factory=list, description="Sessions")
    profiles: List[Dict[str, Any]] = Field(default_factory=list, description="Profiles")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Health status")
    timestamp: str = Field(..., description="Current timestamp")
    database_exists: bool = Field(..., description="Database file exists")
    storage_exists: bool = Field(..., description="Storage file exists")

class ApiResponse(BaseModel):
    message: str = Field(..., description="Response message")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Response timestamp")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")

class CookieResponse(BaseModel):
    cookies: List[CookieModel] = Field(..., description="List of cookies")
    count: int = Field(..., description="Number of cookies")

class SessionCreateRequest(BaseModel):
    name: str = Field(..., description="Session name")
    description: str = Field(default="", description="Session description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class DashboardStats(BaseModel):
    total_cookies: int = Field(..., description="Total number of cookies")
    total_sessions: int = Field(..., description="Total number of sessions")
    unique_domains: int = Field(..., description="Number of unique domains")
    last_updated: str = Field(..., description="Last update timestamp")
    storage_size: str = Field(..., description="Storage file size")
