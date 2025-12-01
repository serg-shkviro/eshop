.PHONY: help install run dev seed docker-build docker-up docker-down docker-logs docker-migrate docker-migration docker-shell db-shell docker-seed clean test

# Default target
help:
	@echo "Available commands:"
	@echo "  make install          - Install dependencies"
	@echo "  make run              - Run the application locally"
	@echo "  make dev              - Run with hot-reload"
	@echo "  make seed             - Seed database with sample data"
	@echo "  make demo-cart        - Demo shopping cart functionality (requires running server)"
	@echo "  make demo-auth        - Demo authentication flow (requires running server)"
	@echo "  make clean-old        - Remove old files from root directory"
	@echo "  make docker-build     - Build Docker images"
	@echo "  make docker-up        - Start Docker containers"
	@echo "  make docker-down      - Stop Docker containers"
	@echo "  make docker-logs      - View Docker logs"
	@echo "  make docker-migrate   - Run database migrations in Docker"
	@echo "  make docker-migration - Create new migration in Docker"
	@echo "  make docker-seed      - Seed database in Docker"
	@echo "  make docker-shell     - Access application shell in Docker"
	@echo "  make db-shell         - Access PostgreSQL shell in Docker"
	@echo "  make migrate          - Run database migrations locally"
	@echo "  make migration        - Create new migration locally"
	@echo "  make clean            - Remove cache and build files"
	@echo "  make test             - Run all tests"
	@echo "  make test-cov         - Run tests with coverage report"
	@echo "  make test-fast        - Run tests without coverage"

# Local development
install:
	pip install -r requirements.txt

run:
	python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

dev:
	python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

seed:
	python scripts/seed_data.py

demo-cart:
	python scripts/demo_cart.py

demo-auth:
	python scripts/demo_auth.py

# Database migrations (local)
migrate:
	alembic upgrade head

migration:
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

# Docker commands
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-restart:
	docker-compose restart web

# Docker database operations
docker-migrate:
	docker-compose exec web alembic upgrade head

docker-migration:
	@read -p "Enter migration message: " msg; \
	docker-compose exec web alembic revision --autogenerate -m "$$msg"

docker-seed:
	docker-compose exec web python scripts/seed_data.py

docker-shell:
	docker-compose exec web /bin/bash

db-shell:
	docker-compose exec db psql -U postgres -d myapp

# Production Docker commands
prod-up:
	docker-compose -f docker-compose.prod.yml up -d --build

prod-down:
	docker-compose -f docker-compose.prod.yml down

prod-logs:
	docker-compose -f docker-compose.prod.yml logs -f

prod-migrate:
	docker-compose -f docker-compose.prod.yml exec web alembic upgrade head

# Delete old files from root
clean-old:
	@echo "Cleaning up old files from root directory..."
	@rm -f main.py config.py database.py auth.py models.py schemas.py 2>/dev/null || true
	@rm -f test_auth.py test_cart.py seed_data.py 2>/dev/null || true
	@echo "Old files removed"

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/

# Testing
test:
	pytest

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term

test-fast:
	pytest --no-cov -x

test-verbose:
	pytest -vv

test-auth:
	pytest tests/test_auth.py -v

test-products:
	pytest tests/test_products.py -v

test-cart:
	pytest tests/test_cart.py -v

test-orders:
	pytest tests/test_orders.py -v

test-reviews:
	pytest tests/test_reviews.py -v

# Combined commands for convenience
start: docker-up docker-migrate
	@echo "Application is running at http://localhost:8000"

stop: docker-down
	@echo "Application stopped"

restart: docker-down docker-up docker-migrate
	@echo "Application restarted"

