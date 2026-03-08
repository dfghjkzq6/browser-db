# Browser Storage Database API

A REST API for managing browser storage states and session data with Git-based persistence.

## Quick Start

```bash
# Install dependencies
pip3 install -r requirements.txt

# Start the API server
python3 app.py
# Or use the runner script
./run.sh
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Base Endpoints

- `GET /` - API information and available endpoints
- `GET /health` - Health check and system status

### Database Management

- `GET /database` - Get database metadata and structure
- `PUT /database` - Update database metadata

### Storage State Management

- `GET /storage` - Get current storage state
- `PUT /storage` - Update entire storage state
- `GET /storage/cookies` - Get all cookies
- `POST /storage/cookies` - Add new cookie
- `DELETE /storage/cookies/<name>` - Delete cookie by name

### Session Management

- `GET /sessions` - Get all sessions
- `POST /sessions` - Create new session
- `GET /sessions/<session_id>` - Get specific session
- `DELETE /sessions/<session_id>` - Delete session

## API Usage Examples

### Get All Cookies
```bash
curl http://localhost:5000/storage/cookies
```

### Add a New Cookie
```bash
curl -X POST http://localhost:5000/storage/cookies \
  -H "Content-Type: application/json" \
  -d '{
    "name": "session_id",
    "value": "abc123",
    "domain": ".example.com",
    "path": "/"
  }'
```

### Create a Session
```bash
curl -X POST http://localhost:5000/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Session",
    "description": "Test session for browser automation"
  }'
```

### Update Storage State
```bash
curl -X PUT http://localhost:5000/storage \
  -H "Content-Type: application/json" \
  -d @storagestate.json
```

## Database Structure

The API manages two main files:

- `database.json` - Metadata and session information
- `storagestate.json` - Browser cookies and storage state

### JSON Database Schema

```json
{
  "metadata": {
    "created": "timestamp",
    "version": "string",
    "description": "string"
  },
  "storage_states": {
    "current": {
      "timestamp": "timestamp",
      "source": "string",
      "cookies_count": "number",
      "file": "string"
    }
  },
  "sessions": [
    {
      "id": "uuid",
      "created": "timestamp",
      "name": "string",
      "description": "string",
      "storage_snapshot": {},
      "metadata": {}
    }
  ],
  "profiles": []
}
```

## Files

- `app.py` - Flask REST API application
- `convert_to_storagestate.py` - Script to convert Chromium cookies to storagestate format
- `storagestate.json` - Current browser storage state
- `database.json` - Database metadata and structure
- `requirements.txt` - Python dependencies
- `run.sh` - API server runner script

## Features

- ✅ RESTful API design
- ✅ CORS enabled for web applications
- ✅ Git-based version control
- ✅ Session management
- ✅ Cookie CRUD operations
- ✅ Health monitoring
- ✅ JSON database persistence

## Deployment

The API can be deployed on any platform that supports Python:

- Local development
- Docker containers
- Cloud platforms (Heroku, Vercel, etc.)
- VPS servers

## License

MIT License - feel free to use this for your browser automation projects.
