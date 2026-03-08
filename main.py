#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any
import aiofiles

from models import (
    CookieModel, StorageStateModel, StorageStateInfo, DatabaseMetadata,
    SessionModel, DatabaseModel, HealthResponse, ApiResponse, CookieResponse,
    SessionCreateRequest, DashboardStats, SameSiteEnum
)

app = FastAPI(
    title="Browser Storage Database API",
    description="REST API for managing browser storage states and session data",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DB_FILE = 'database.json'
STORAGE_FILE = 'storagestate.json'

async def load_database() -> DatabaseModel:
    """Load the database from JSON file"""
    try:
        async with aiofiles.open(DB_FILE, 'r') as f:
            content = await f.read()
            data = json.loads(content)
            return DatabaseModel(**data)
    except FileNotFoundError:
        return DatabaseModel(
            metadata=DatabaseMetadata(
                created=datetime.now().isoformat(),
                version="2.0.0",
                description="Browser storage state database"
            )
        )

async def save_database(db: DatabaseModel):
    """Save the database to JSON file"""
    async with aiofiles.open(DB_FILE, 'w') as f:
        await f.write(db.json(indent=2))

async def load_storage_state() -> StorageStateModel:
    """Load storage state from file"""
    try:
        async with aiofiles.open(STORAGE_FILE, 'r') as f:
            content = await f.read()
            data = json.loads(content)
            return StorageStateModel(**data)
    except FileNotFoundError:
        return StorageStateModel()

async def save_storage_state(storage: StorageStateModel):
    """Save storage state to file"""
    async with aiofiles.open(STORAGE_FILE, 'w') as f:
        await f.write(storage.json(indent=2))

def get_file_size(filepath: str) -> str:
    """Get human readable file size"""
    try:
        size = os.path.getsize(filepath)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    except:
        return "0 B"

# Dashboard Routes
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Admin dashboard"""
    db = await load_database()
    storage = await load_storage_state()
    
    # Calculate stats
    unique_domains = len(set(cookie.domain for cookie in storage.cookies))
    stats = DashboardStats(
        total_cookies=len(storage.cookies),
        total_sessions=len(db.sessions),
        unique_domains=unique_domains,
        last_updated=db.storage_states.get('current', {}).get('timestamp', 'Unknown'),
        storage_size=get_file_size(STORAGE_FILE)
    )
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "cookies": storage.cookies[:20],  # Show first 20 cookies
        "sessions": db.sessions[:10],    # Show first 10 sessions
        "total_cookies": len(storage.cookies),
        "total_sessions": len(db.sessions)
    })

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        database_exists=os.path.exists(DB_FILE),
        storage_exists=os.path.exists(STORAGE_FILE)
    )

# API Routes
@app.get("/api/database", response_model=DatabaseModel)
async def get_database():
    """Get database metadata and structure"""
    return await load_database()

@app.put("/api/database")
async def update_database(metadata: DatabaseMetadata):
    """Update database metadata"""
    db = await load_database()
    db.metadata = metadata
    db.metadata.updated = datetime.now().isoformat()
    await save_database(db)
    return db

@app.get("/api/storage", response_model=StorageStateModel)
async def get_storage():
    """Get current storage state"""
    return await load_storage_state()

@app.put("/api/storage")
async def update_storage(storage: StorageStateModel):
    """Update entire storage state"""
    await save_storage_state(storage)
    
    # Update database metadata
    db = await load_database()
    db.storage_states['current'] = StorageStateInfo(
        timestamp=datetime.now().isoformat(),
        source="api",
        cookies_count=len(storage.cookies),
        file=STORAGE_FILE
    )
    await save_database(db)
    
    return ApiResponse(
        message="Storage state updated",
        data={"cookies_count": len(storage.cookies)}
    )

@app.get("/api/storage/cookies", response_model=CookieResponse)
async def get_cookies():
    """Get all cookies"""
    storage = await load_storage_state()
    return CookieResponse(cookies=storage.cookies, count=len(storage.cookies))

@app.post("/api/storage/cookies", response_model=ApiResponse)
async def add_cookie(cookie: CookieModel):
    """Add a new cookie"""
    storage = await load_storage_state()
    
    # Check if cookie already exists and remove it
    storage.cookies = [c for c in storage.cookies if c.name != cookie.name]
    
    # Add new cookie
    storage.cookies.append(cookie)
    await save_storage_state(storage)
    
    return ApiResponse(
        message="Cookie added",
        data={
            "cookie": cookie.dict(),
            "total_cookies": len(storage.cookies)
        }
    )

@app.delete("/api/storage/cookies/{cookie_name}", response_model=ApiResponse)
async def delete_cookie(cookie_name: str):
    """Delete a cookie by name"""
    storage = await load_storage_state()
    original_count = len(storage.cookies)
    
    storage.cookies = [c for c in storage.cookies if c.name != cookie_name]
    deleted_count = original_count - len(storage.cookies)
    
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Cookie '{cookie_name}' not found")
    
    await save_storage_state(storage)
    
    return ApiResponse(
        message=f"Cookie '{cookie_name}' deleted",
        data={
            "deleted_count": deleted_count,
            "remaining_cookies": len(storage.cookies)
        }
    )

@app.get("/api/sessions", response_model=List[SessionModel])
async def get_sessions():
    """Get all sessions"""
    db = await load_database()
    return db.sessions

@app.post("/api/sessions", response_model=SessionModel)
async def create_session(session_data: SessionCreateRequest):
    """Create a new session"""
    db = await load_database()
    storage = await load_storage_state()
    
    session_id = str(uuid.uuid4())
    new_session = SessionModel(
        id=session_id,
        created=datetime.now().isoformat(),
        name=session_data.name,
        description=session_data.description,
        storage_snapshot=storage,
        metadata=session_data.metadata
    )
    
    db.sessions.append(new_session)
    await save_database(db)
    
    return new_session

@app.get("/api/sessions/{session_id}", response_model=SessionModel)
async def get_session(session_id: str):
    """Get a specific session"""
    db = await load_database()
    session = next((s for s in db.sessions if s.id == session_id), None)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session

@app.delete("/api/sessions/{session_id}", response_model=ApiResponse)
async def delete_session(session_id: str):
    """Delete a session"""
    db = await load_database()
    original_count = len(db.sessions)
    
    db.sessions = [s for s in db.sessions if s.id != session_id]
    deleted_count = original_count - len(db.sessions)
    
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    
    await save_database(db)
    
    return ApiResponse(
        message=f"Session {session_id} deleted",
        data={
            "deleted_count": deleted_count,
            "remaining_sessions": len(db.sessions)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
