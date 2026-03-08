#!/usr/bin/env python3
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)

DB_FILE = 'database.json'
STORAGE_FILE = 'storagestate.json'

def load_database():
    """Load the database from JSON file"""
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "metadata": {
                "created": datetime.now().isoformat(),
                "version": "1.0.0",
                "description": "Browser storage state database"
            },
            "storage_states": {},
            "sessions": [],
            "profiles": []
        }

def save_database(data):
    """Save the database to JSON file"""
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_storage_state():
    """Load storage state from file"""
    try:
        with open(STORAGE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"cookies": [], "origins": []}

def save_storage_state(data):
    """Save storage state to file"""
    with open(STORAGE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def index():
    """API Root - Show available endpoints"""
    return jsonify({
        "name": "Browser Storage Database API",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "API information",
            "GET /health": "Health check",
            "GET /database": "Get database metadata",
            "GET /storage": "Get current storage state",
            "PUT /storage": "Update storage state",
            "GET /storage/cookies": "Get cookies only",
            "POST /storage/cookies": "Add new cookie",
            "DELETE /storage/cookies/<name>": "Delete cookie by name",
            "GET /sessions": "Get all sessions",
            "POST /sessions": "Create new session",
            "GET /sessions/<session_id>": "Get specific session",
            "DELETE /sessions/<session_id>": "Delete session"
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database_exists": os.path.exists(DB_FILE),
        "storage_exists": os.path.exists(STORAGE_FILE)
    })

@app.route('/database', methods=['GET'])
def get_database():
    """Get database metadata and structure"""
    db = load_database()
    return jsonify(db)

@app.route('/database', methods=['PUT'])
def update_database():
    """Update database metadata"""
    db = load_database()
    data = request.get_json()
    
    if 'metadata' in data:
        db['metadata'].update(data['metadata'])
    
    db['metadata']['updated'] = datetime.now().isoformat()
    save_database(db)
    
    return jsonify(db)

@app.route('/storage', methods=['GET'])
def get_storage():
    """Get current storage state"""
    storage = load_storage_state()
    return jsonify(storage)

@app.route('/storage', methods=['PUT'])
def update_storage():
    """Update entire storage state"""
    data = request.get_json()
    
    if not data:
        abort(400, description="Invalid JSON data")
    
    save_storage_state(data)
    
    # Update database metadata
    db = load_database()
    db['storage_states']['current'] = {
        "timestamp": datetime.now().isoformat(),
        "source": "api",
        "cookies_count": len(data.get('cookies', [])),
        "file": STORAGE_FILE
    }
    save_database(db)
    
    return jsonify({
        "message": "Storage state updated",
        "timestamp": datetime.now().isoformat(),
        "cookies_count": len(data.get('cookies', []))
    })

@app.route('/storage/cookies', methods=['GET'])
def get_cookies():
    """Get all cookies"""
    storage = load_storage_state()
    return jsonify({
        "cookies": storage.get('cookies', []),
        "count": len(storage.get('cookies', []))
    })

@app.route('/storage/cookies', methods=['POST'])
def add_cookie():
    """Add a new cookie"""
    storage = load_storage_state()
    cookie_data = request.get_json()
    
    if not cookie_data or 'name' not in cookie_data:
        abort(400, description="Cookie data required with 'name' field")
    
    # Check if cookie already exists and remove it
    storage['cookies'] = [c for c in storage.get('cookies', []) 
                         if c['name'] != cookie_data['name']]
    
    # Add new cookie with defaults
    new_cookie = {
        "name": cookie_data['name'],
        "value": cookie_data.get('value', ''),
        "domain": cookie_data.get('domain', ''),
        "path": cookie_data.get('path', '/'),
        "expires": cookie_data.get('expires', -1),
        "httpOnly": cookie_data.get('httpOnly', False),
        "secure": cookie_data.get('secure', True),
        "sameSite": cookie_data.get('sameSite', 'Lax')
    }
    
    storage['cookies'].append(new_cookie)
    save_storage_state(storage)
    
    return jsonify({
        "message": "Cookie added",
        "cookie": new_cookie,
        "total_cookies": len(storage['cookies'])
    })

@app.route('/storage/cookies/<cookie_name>', methods=['DELETE'])
def delete_cookie(cookie_name):
    """Delete a cookie by name"""
    storage = load_storage_state()
    original_count = len(storage.get('cookies', []))
    
    storage['cookies'] = [c for c in storage.get('cookies', []) 
                         if c['name'] != cookie_name]
    
    deleted_count = original_count - len(storage['cookies'])
    
    if deleted_count == 0:
        abort(404, description=f"Cookie '{cookie_name}' not found")
    
    save_storage_state(storage)
    
    return jsonify({
        "message": f"Cookie '{cookie_name}' deleted",
        "deleted_count": deleted_count,
        "remaining_cookies": len(storage['cookies'])
    })

@app.route('/sessions', methods=['GET'])
def get_sessions():
    """Get all sessions"""
    db = load_database()
    return jsonify({
        "sessions": db.get('sessions', []),
        "count": len(db.get('sessions', []))
    })

@app.route('/sessions', methods=['POST'])
def create_session():
    """Create a new session"""
    db = load_database()
    session_data = request.get_json()
    
    session_id = str(uuid.uuid4())
    new_session = {
        "id": session_id,
        "created": datetime.now().isoformat(),
        "name": session_data.get('name', f"Session {len(db['sessions']) + 1}"),
        "description": session_data.get('description', ''),
        "storage_snapshot": load_storage_state(),
        "metadata": session_data.get('metadata', {})
    }
    
    db['sessions'].append(new_session)
    save_database(db)
    
    return jsonify(new_session), 201

@app.route('/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get a specific session"""
    db = load_database()
    session = next((s for s in db.get('sessions', []) if s['id'] == session_id), None)
    
    if not session:
        abort(404, description="Session not found")
    
    return jsonify(session)

@app.route('/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a session"""
    db = load_database()
    original_count = len(db.get('sessions', []))
    
    db['sessions'] = [s for s in db.get('sessions', []) if s['id'] != session_id]
    deleted_count = original_count - len(db['sessions'])
    
    if deleted_count == 0:
        abort(404, description="Session not found")
    
    save_database(db)
    
    return jsonify({
        "message": f"Session {session_id} deleted",
        "deleted_count": deleted_count,
        "remaining_sessions": len(db['sessions'])
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
