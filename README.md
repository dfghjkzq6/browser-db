# Browser Storage Database API

A FastAPI-based REST API with admin dashboard for managing browser storage states and session data with Git-based persistence.

## Quick Start

```bash
# Install dependencies
pip3 install -r requirements.txt

# Start the API server
python3 main.py
# Or use the runner script
./run.sh
```

The API will be available at:
- **Dashboard:** `http://localhost:8000`
- **API Documentation:** `http://localhost:8000/docs`
- **Health Check:** `http://localhost:8000/health`

## 🎯 Features

### For Non-Technical Users
- **Beautiful Admin Dashboard** - User-friendly web interface
- **Visual Statistics** - Real-time charts and metrics
- **One-Click Operations** - Add/delete cookies, create sessions
- **Export Functionality** - Download data with one click
- **Responsive Design** - Works on desktop and mobile

### For Technical Users
- **FastAPI Backend** - High-performance async API
- **Pydantic Validation** - Type-safe data models
- **Auto-generated Docs** - Interactive API documentation
- **RESTful Design** - Clean, standard endpoints
- **Git Integration** - Version control for all data

## 📊 Dashboard Features

### Overview Statistics
- Total cookies count
- Active sessions
- Unique domains
- Storage file size

### Cookie Management
- View all cookies with details
- Add new cookies with form validation
- Delete cookies with confirmation
- Filter by domain and security settings

### Session Management
- Create session snapshots
- View session details
- Delete old sessions
- Export session data

### Quick Actions
- Refresh data
- Export storage state
- Access API documentation
- Health monitoring

## 🚀 API Endpoints

### Base Endpoints
- `GET /` - Admin dashboard (HTML)
- `GET /health` - Health check and system status
- `GET /docs` - Interactive API documentation

### Database Management
- `GET /api/database` - Get database metadata and structure
- `PUT /api/database` - Update database metadata

### Storage State Management
- `GET /api/storage` - Get current storage state
- `PUT /api/storage` - Update entire storage state
- `GET /api/storage/cookies` - Get all cookies
- `POST /api/storage/cookies` - Add new cookie
- `DELETE /api/storage/cookies/<name>` - Delete cookie by name

### Session Management
- `GET /api/sessions` - Get all sessions
- `POST /api/sessions` - Create new session
- `GET /api/sessions/<session_id>` - Get specific session
- `DELETE /api/sessions/<session_id>` - Delete session

## 📖 API Usage Examples

### Get All Cookies
```bash
curl http://localhost:8000/api/storage/cookies
```

### Add a New Cookie
```bash
curl -X POST http://localhost:8000/api/storage/cookies \
  -H "Content-Type: application/json" \
  -d '{
    "name": "session_id",
    "value": "abc123",
    "domain": ".example.com",
    "path": "/",
    "secure": true,
    "httpOnly": false
  }'
```

### Create a Session
```bash
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Session",
    "description": "Test session for browser automation"
  }'
```

### Update Storage State
```bash
curl -X PUT http://localhost:8000/api/storage \
  -H "Content-Type: application/json" \
  -d @storagestate.json
```

## 🏗️ Project Structure

```
BrowserUse/
├── main.py                 # FastAPI application
├── models.py              # Pydantic data models
├── requirements.txt       # Python dependencies
├── run.sh                # Startup script
├── database.json         # Database metadata
├── storagestate.json     # Browser storage state
├── templates/            # HTML templates
│   └── dashboard.html    # Admin dashboard
├── static/               # Static assets
│   └── css/
│       └── custom.css    # Custom styling
└── convert_to_storagestate.py  # Utility script
```

## 🔧 Data Models

### Cookie Model
```python
class CookieModel(BaseModel):
    name: str
    value: str = ""
    domain: str
    path: str = "/"
    expires: int = -1
    httpOnly: bool = False
    secure: bool = True
    sameSite: Optional[SameSiteEnum] = None
```

### Session Model
```python
class SessionModel(BaseModel):
    id: str
    created: str
    name: str
    description: str = ""
    storage_snapshot: StorageStateModel
    metadata: Dict[str, Any] = {}
```

## 🌟 Advanced Features

### Pydantic Validation
- Type-safe data models
- Automatic validation
- Clear error messages
- OpenAPI schema generation

### Async Performance
- Fast async/await support
- Concurrent request handling
- Better resource utilization

### Admin Dashboard
- Modern Bootstrap 5 design
- Responsive layout
- Interactive components
- Real-time updates

### Git Integration
- Automatic version control
- Change tracking
- Rollback capability
- Collaboration support

## 🚀 Deployment

### Local Development
```bash
python3 main.py
```

### Production with Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Platforms
- **Heroku:** Works out of the box
- **Vercel:** Serverless deployment
- **AWS:** ECS or Lambda
- **DigitalOcean:** App Platform

## 🔒 Security Features

- CORS enabled for web applications
- Input validation with Pydantic
- Secure cookie handling
- No sensitive data exposure
- Rate limiting ready

## 📈 Monitoring

### Health Check Endpoint
```json
{
  "status": "healthy",
  "timestamp": "2026-03-08T12:00:00Z",
  "database_exists": true,
  "storage_exists": true
}
```

### Dashboard Statistics
- Real-time cookie count
- Session tracking
- Storage usage
- System health indicators

## 🔄 Migration from Flask

If you're migrating from the Flask version:

1. **Dependencies:** Update `requirements.txt`
2. **Main File:** Replace `app.py` with `main.py`
3. **Models:** Add `models.py` with Pydantic schemas
4. **Templates:** Use new dashboard template
5. **Static Files:** Add custom CSS styling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - feel free to use this for your browser automation projects.

## 🆘 Support

- **Issues:** Report bugs on GitHub
- **Documentation:** Check `/docs` endpoint
- **Health:** Monitor `/health` endpoint
- **Dashboard:** Use web interface for easy management
