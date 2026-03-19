.PHONY: help dev test lint format migrate docker-up docker-down install

help: ## Mostrar ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instalar dependencias
	uv sync
	cd frontend && npm install

dev: ## Iniciar servidor de desarrollo
	uvicorn galleguimetro.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Iniciar frontend de desarrollo
	cd frontend && npm start

test: ## Ejecutar tests
	pytest tests/ -v --tb=short

test-unit: ## Ejecutar tests unitarios
	pytest tests/unit/ -v

test-integration: ## Ejecutar tests de integración
	pytest tests/integration/ -v

lint: ## Ejecutar linter
	ruff check galleguimetro/ tests/

format: ## Formatear código
	ruff format galleguimetro/ tests/

type-check: ## Verificar tipos
	mypy galleguimetro/

migrate: ## Ejecutar migraciones
	alembic upgrade head

migrate-create: ## Crear nueva migración (usar: make migrate-create MSG="descripcion")
	alembic revision --autogenerate -m "$(MSG)"

docker-up: ## Iniciar servicios Docker (postgres + qdrant)
	docker compose up -d

docker-down: ## Detener servicios Docker
	docker compose down

docker-prod: ## Construir y ejecutar en producción
	docker compose -f docker-compose.prod.yml up --build -d

clean: ## Limpiar archivos temporales
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
