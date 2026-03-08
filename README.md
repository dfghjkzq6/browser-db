# Browser Storage Database

A Git-based database for managing browser storage states and session data.

## Structure

- `database.json` - Main database file with metadata and references
- `storagestate.json` - Browser cookies and storage state
- `sessions/` - Individual session files (if needed)
- `profiles/` - Browser profile configurations

## Usage

This repository serves as a database for browser automation and state management.

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
  "sessions": [],
  "profiles": []
}
```

## Files

- `convert_to_storagestate.py` - Script to convert Chromium cookies to storagestate format
- `storagestate.json` - Current browser storage state
- `database.json` - Database metadata and structure
