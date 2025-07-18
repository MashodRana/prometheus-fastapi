# FastAPI Production App with Prometheus Metrics

This project is a production-ready FastAPI application with PostgreSQL, SQLAlchemy, and Prometheus metrics integration. It is containerized using Docker and supports async database operations, user management, and detailed metrics for both HTTP and system-level monitoring.

## Features

- **FastAPI**: High-performance Python web framework.
- **Async SQLAlchemy**: Asynchronous ORM for PostgreSQL.
- **Alembic**: Database migrations.
- **Prometheus Metrics**: HTTP and system metrics exposed at `/metrics`.
- **Dockerized**: Easy deployment with Docker and Docker Compose.
- **User Management**: CRUD endpoints for users.
- **CORS**: Configurable CORS origins.
- **Health Check**: `/health` endpoint for readiness/liveness probes.

## Project Structure

```
.
├── app/
│   ├── api/                # API routers and views
│   ├── core/               # Core config, database, main app factory
│   ├── metrics/            # Prometheus metrics (HTTP/system)
│   ├── middlewares/        # Custom middlewares (metrics, etc.)
│   ├── models/             # SQLAlchemy models
│   └── schemas/            # Pydantic schemas
├── alembic/                # Alembic migrations
├── prometheus/             # Prometheus config
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── server.py               # Entrypoint for running the app
└── README.md
```

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.13+ (for local development)

### Environment Variables

Copy `.env.example` to `.env` and adjust as needed.

### Build and Run with Docker

```sh
docker-compose up --build
```

- FastAPI app: [http://localhost:8000](http://localhost:8000)
- Prometheus: [http://localhost:9090](http://localhost:9090)
- Metrics endpoint: [http://localhost:8000/metrics](http://localhost:8000/metrics)
- Health check: [http://localhost:8000/health](http://localhost:8000/health)

### Database Migrations

Alembic is used for migrations. On container startup, migrations are applied automatically.

To run manually:

```sh
alembic upgrade head
```

### API Usage

- **User Endpoints**: `/api/v1/users/`

Create user with `POST` method
```
{
  "email": "user@example.com",
  "username": "string",
  "full_name": "string",
  "bio": "string",
  "is_active": true,
  "password": "stringst"
}
```
Get all user with `GET` method with query params `page`, `limit`
- **Get One user info**: `/api/users/{user_id}/`
- **OpenAPI Docs**: `/api/docs/` (not available in production)
- **Redoc**: `/api/redoc/` (not available in production)

### Metrics

- **HTTP Metrics**: Request count, duration, size, exceptions, etc.
- **System Metrics**: CPU, memory, threads, GC, file descriptors, etc.
- **Prometheus Scrape**: Configured in [`prometheus/prometheus.yml`](prometheus/prometheus.yml)

### Development

- Edit code in the `app/` directory.
- Hot reload is enabled by default in development.
- Logging is configured via the `LOG_LEVEL` setting.

## Configuration

All settings are managed via [`app/core/config.py`](app/core/config.py) and `.env` file.
