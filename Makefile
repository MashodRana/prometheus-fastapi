.PHONY: help build up down logs shell migrate test lint format clean

# Default target
help:
	@echo "Available commands:"
	@echo "  build      - Build Docker images"
	@echo "  up         - Start all services"
	@echo "  down       - Stop all services"
	@echo "  logs       - Show logs"
	@echo "  shell      - Access app container shell"
	@echo "  migrate    - Run database migrations"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linting"
	@echo "  format     - Format code"
	@echo "  clean      - Clean up containers and volumes"

# Build Docker images
build:
	docker-compose build

# Start all services
up:
	docker-compose up -d

# Stop all services
down:
	docker-compose down

# Show logs
logs:
	docker-compose logs -f

# Access app container shell
shell:
	docker-compose exec app bash

# Run database migrations
migrate:
	docker-compose exec app alembic upgrade head

# Create new migration
migration:
	docker-compose exec app alembic revision --autogenerate -m "$(msg)"

# Run tests
test:
	docker-compose exec app python -m pytest

# Run linting
lint:
	docker-compose exec app flake8 app/
	docker-compose exec app mypy app/

# Format code
format:
	docker-compose exec app black app/
	docker-compose exec app isort app/

# Clean up
clean:
	docker-compose down -v
	docker system prune -f

# Development setup
dev-setup:
	cp .env.example .env
	docker-compose build
	docker-compose up -d
	sleep 10
	docker-compose exec app alembic upgrade head

# Production deployment
prod-deploy:
	docker-compose -f docker-compose.yml build
	docker-compose -f docker-compose.yml up -d
	docker-compose exec app alembic upgrade head