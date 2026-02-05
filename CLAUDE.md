# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ZavodHelper is a manufacturing knowledge base web application for managing production-related information (instructions and incidents) in Russian-speaking industrial environments. It serves as a centralized knowledge management system for factory floor operations.

## Development Commands

```bash
# Setup
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux/Mac
pip install -r requirements.txt

# Initialize database with demo data
python scripts/init_db.py

# Run development server (http://localhost:8000)
python run.py

# Run tests
pytest tests/

# Docker deployment
docker-compose up -d
```

## Tech Stack

- **Backend**: FastAPI + Uvicorn (Python 3.11+)
- **Database**: SQLite (default), SQLAlchemy 2.0 ORM
- **Templates**: Jinja2 server-side rendering
- **Frontend**: Vanilla JavaScript, no framework
- **Validation**: Pydantic v2
- **Image Processing**: Pillow (converts to WebP, max 800x600)

## Architecture

```
app/
├── main.py          # FastAPI app init, lifespan management
├── config.py        # Environment configuration
├── database.py      # SQLAlchemy setup, session management
├── models/          # SQLAlchemy ORM models
├── schemas/         # Pydantic request/response schemas
├── crud/            # Database operations layer
├── routers/         # API and HTML route handlers
│   ├── api.py       # REST API endpoints (/api/*)
│   ├── pages.py     # HTML pages (/, /editor)
│   └── upload.py    # Image upload processing
└── static/          # CSS, JS assets
```

**Data Model**: Item → Pages → Actions (hierarchical with cascade deletes)
- **Item**: Incident or Instruction (title, type, timestamps)
- **Page**: Step within an item (title, time estimate, image, order)
- **Action**: Individual action within a page (text, order)

## Key Patterns

- **Layered Architecture**: Routes → CRUD → Database → Models
- **Async/Await**: Full async support with FastAPI and aiofiles
- **Dependency Injection**: FastAPI's `Depends()` for database sessions
- **Eager Loading**: SQLAlchemy `joinedload` for relationships

## API Endpoints

- `GET/POST /api/items` - List/create items
- `GET/PUT/DELETE /api/items/{id}` - Single item operations
- `GET /api/items/search?q=<query>` - Search by title
- `GET /api/incidents` | `GET /api/instructions` - Type-filtered lists
- `GET /api/export` | `POST /api/import` - JSON backup/restore
- `POST /api/upload` - Image upload (converts to WebP)
- `DELETE /api/clear?confirm=true` - Clear all data

## HTML Pages

- `/` - Viewer page (dark theme, read-only)
- `/editor` - Editor page (light theme, full CRUD)

## Configuration (Environment Variables)

- `HOST` (default: "0.0.0.0")
- `PORT` (default: 8000)
- `DEBUG` (default: "true")
- `DATABASE_URL` (default: "sqlite:///./zavod.db")
- `UPLOAD_DIR` (default: "uploads/")

## Testing

Tests use in-memory SQLite configured in `tests/conftest.py`. Run single test:
```bash
pytest tests/test_api.py::test_name -v
```
