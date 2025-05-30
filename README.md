# PDF Parser Service

A clean, production-ready FastAPI service for parsing PDF files to Markdown using MarkItDown library with Celery for asynchronous processing.

## Features

- 🚀 FastAPI with async/await support
- 📄 PDF to Markdown conversion using MarkItDown
- ⚡ Asynchronous processing with Celery
- 🔄 Both sync and async parsing endpoints
- 🐳 Docker Compose for Redis
- 📝 Clean code architecture with proper separation of concerns
- 🔍 Comprehensive error handling and logging
- 📊 Task result tracking

## Architecture

```
app/
├── api/
│   └── routes.py          # FastAPI endpoints
├── services/
│   └── pdf_parser.py      # Core PDF parsing logic
├── models.py              # Pydantic models
├── worker.py              # Celery worker
└── main.py                # FastAPI application
```

## Setup

### Prerequisites

- Python 3.10+
- uv package manager
- Docker (for Redis)

### Installation

1. Clone and navigate to the project:
```bash
cd grading-pdf
```

2. Create virtual environment with uv:
```bash
uv venv --python=3.10 .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
uv pip install -e .
```

4. Start Redis with Docker Compose:
```bash
docker-compose up -d redis
```

## Running the Service

### Option 1: Docker Compose (Recommended)
```bash
# One-command startup
./scripts/start.sh

# Or manually
docker compose up -d
```

### Option 2: Development Mode
```bash
# 1. Start Redis
docker compose up -d redis

# 2. Start FastAPI server
python run.py

# 3. Start Celery worker (separate terminal)
python scripts/start_worker.py
```

## API Endpoints

### POST `/api/v1/parse` - Async PDF Parsing
Upload a PDF for asynchronous parsing:

```bash
curl -X POST "http://localhost:8000/api/v1/parse" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf" \
  -F "user_id=user123" \
  -F "file_id=file456"
```

Response:
```json
{
  "task_id": "abc123-def456",
  "status": "pending",
  "message": "PDF parsing task submitted successfully"
}
```

### POST `/api/v1/parse/sync` - Sync PDF Parsing
Parse PDF synchronously (for smaller files):

```bash
curl -X POST "http://localhost:8000/api/v1/parse/sync" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf" \
  -F "user_id=user123"
```

### GET `/api/v1/task/{task_id}` - Get Task Result
Check the status and result of an async parsing task:

```bash
curl "http://localhost:8000/api/v1/task/abc123-def456"
```

Response:
```json
{
  "task_id": "abc123-def456",
  "status": "success",
  "content": "# Document Title\n\nParsed content...",
  "user_id": "user123",
  "file_id": "file456",
  "error": null
}
```

### GET `/api/v1/health` - Health Check
```bash
curl "http://localhost:8000/api/v1/health"
```

## Development

### API Documentation
Visit http://localhost:8000/docs for interactive API documentation.

### Testing
```bash
uv pip install pytest httpx pytest-asyncio
pytest
```

### Code Structure

- **Clean Architecture**: Separated concerns with dedicated service layer
- **Error Handling**: Custom exceptions and comprehensive error responses
- **Logging**: Structured logging throughout the application
- **Type Hints**: Full type annotation for better IDE support
- **Async/Await**: Proper async handling for file operations

## Configuration

The service uses environment variables for configuration:

- `REDIS_URL`: Redis connection URL (default: redis://localhost:6379)
- `CELERY_BROKER_URL`: Celery broker URL (default: redis://localhost:6379)
- `LOG_LEVEL`: Logging level (default: INFO)

## Production Considerations

- Configure proper CORS origins in `app/main.py`
- Set up proper logging configuration
- Use environment variables for Redis connection
- Consider using a reverse proxy (nginx)
- Set up monitoring and health checks
- Configure proper file size limits
