# FastAPI Template

A production-ready FastAPI template with modern Python tooling, featuring modular architecture, dependency injection, structured logging, and comprehensive configuration management. Built for scalability and maintainability with best practices baked in.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Logging](#logging)
- [Running the App](#running-the-app)
- [Development](#development)
- [License](#license)

## Features

- **Modern Python tooling** with [uv](https://github.com/astral-sh/uv) for fast dependency management
- **Modular feature-based architecture** for clean code organization
- **Pydantic settings** with cached dependency injection for configuration management
- **Structured logging** with console, file, and JSON output options
- **CORS middleware** with configurable origins for cross-origin requests
- **OpenAPI documentation** with Swagger UI (`/docs`) and ReDoc (`/redoc`)
- **Docker-ready** with optimized containerization
- **CI/CD friendly** with pre-commit hooks and automated testing
- **Environment-based configuration** for different deployment stages
- **Type safety** with comprehensive type hints throughout

## Project Structure

```
fastapi-template/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Pydantic settings and configuration
│   │   ├── dependencies.py     # Cached dependency injection
│   │   └── logging.py          # Structured logging setup
│   └── features/
│       ├── __init__.py
│       ├── health/             # Health check feature example
│       │   ├── __init__.py
│       │   └── router.py
│       └── users/              # Users feature example
│           ├── __init__.py
│           ├── models.py
│           ├── router.py
│           └── service.py
fixtures
│   └── features/
│       ├── test_health.py
│       └── test_users.py
├── run.py                      # Application runner script
├── pyproject.toml              # Project dependencies and tools config
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore patterns
└── README.md
```

## Getting Started

### Prerequisites

- **Python ≥ 3.11**
- **uv** (recommended) or **pip** for dependency management

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kunj-10/fastapi-template.git
   cd fastapi-template
   ```

2. **Install dependencies using uv (recommended):**
   ```bash
   uv sync
   ```

   **Or using pip with virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```

4. **Edit `.env` file with your configuration values**

## Configuration

The application uses environment-based configuration with sensible defaults. Copy `.env.example` to `.env` and customize as needed:

```bash
# Application Settings
APP_NAME=FastAPI Template
ENVIRONMENT=DEV # "DEV", "PROD", "STAGING"

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=plain # "plain", "json"
LOG_FILE=logs/app.log

# CORS Settings
CORS_ORIGINS=["*"]
CORS_ALLOW_CREDENTIALS=True
```

### Configuration Options

- **`APP_NAME`**: Application name displayed in OpenAPI docs
- **`ENVIRONMENT`**: Deployment environment (`DEV`, `PROD`, `STAGING`)
- **`LOG_LEVEL`**: Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)
- **`LOG_FORMAT`**: Log output format (`plain`, `json`)
- **`LOG_FILE`**: Path to log file (directory auto-created if missing)
- **`CORS_ORIGINS`**: List of allowed CORS origins
- **`CORS_ALLOW_CREDENTIALS`**: Allow credentials in CORS requests

## Logging

The template includes comprehensive structured logging:

- **deafult logging**: Human-readable logs for development
- **File logging**: Persistent logs stored in specified file path
- **JSON logging**: Structured logs for production environments and log aggregation
- **Automatic directory creation**: Log directories are created automatically if they don't exist
- **Configurable levels**: Set appropriate log levels per environment

Example log outputs:

**Standard format:**
```
2024-01-15 10:30:45 | INFO | uvicorn.error | Started server process [12345]
```

**JSON format:**
```json
{"timestamp": "2024-01-15T10:30:45.123Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [12345]"}
```

## Running the App

### Development Server

Start the development server with hot reload:

```bash
uv run run.py
```

The application will be available at:
- **API**: http://localhost:8000
- **Interactive API docs (Swagger UI)**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc

### Production Server

For production deployment, use a WSGI server like Gunicorn:

```bash
uv run gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Development

### Code Quality Tools

The project uses **Ruff** for linting and formatting:

1. **Run linting and formatting:**
   ```bash
   uv run ruff check .
   uv run ruff format .
   ```

### Dependency Injection

The template uses cached dependency injection for efficient configuration access:

```python
from app.core.dependencies import SettingsDep

@router.get("/")
def read_root(settings: SettingsDep):
    return {"app_name": settings.app_name, "environment": settings.environment}
```

### Adding New Features

1. Create a new directory under `app/features/`
2. Add router, models, and service modules as needed
3. Include the router in `app/main.py`:
   ```python
   from app.features.your_feature.router import router as your_feature_router
   app.include_router(your_feature_router, prefix="/api/v1/your-feature", tags=["Your Feature"])
   ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Ready to build something amazing?** 🚀

This template provides a solid foundation for your FastAPI projects with production-ready patterns and modern Python tooling. Happy coding!# Insights
# bhoomigundecha
