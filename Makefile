.PHONY: help build up down restart logs shell test migrate makemigrations clean dev prod

# Цвета для вывода
YELLOW := \033[1;33m
GREEN := \033[1;32m
RESET := \033[0m

# По умолчанию показываем help
.DEFAULT_GOAL := help

help: ## Показать все доступные команды
	@echo "$(GREEN)Доступные команды:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-18s$(RESET) %s\n", $$1, $$2}'

# ==================== Docker ====================

build: ## Собрать Docker образы
	docker-compose build

up: ## Поднять все сервисы в фоне
	docker-compose up -d

down: ## Остановить и удалить контейнеры
	docker-compose down

restart: ## Перезапустить все сервисы
	docker-compose restart

stop: ## Остановить контейнеры (не удаляя)
	docker-compose stop

logs: ## Показать логи всех сервисов (Ctrl+C для выхода)
	docker-compose logs -f

logs-app: ## Показать логи только приложения
	docker-compose logs -f app

ps: ## Показать статус контейнеров
	docker-compose ps

# ==================== Development ====================

dev: ## Запустить в dev режиме (с rebuild)
	docker-compose up --build

shell: ## Открыть bash в контейнере app
	docker-compose exec app bash

shell-db: ## Открыть psql в Postgres
	docker-compose exec postgres psql -U postgres -d fitmetrics

python: ## Открыть Python REPL в контейнере
	docker-compose exec app python

# ==================== Database ====================

migrate: ## Применить миграции Alembic
	docker-compose exec app alembic upgrade head

makemigrations: ## Создать новую миграцию (использование: make makemigrations m="описание")
	docker-compose exec app alembic revision --autogenerate -m "$(m)"

downgrade: ## Откатить последнюю миграцию
	docker-compose exec app alembic downgrade -1

db-reset: ## Пересоздать БД (УДАЛИТ ВСЕ ДАННЫЕ!)
	docker-compose down -v
	docker-compose up -d postgres redis
	@echo "$(YELLOW)Ждём запуска Postgres...$(RESET)"
	@sleep 3
	docker-compose up -d app
	$(MAKE) migrate

# ==================== Testing ====================

test: ## Запустить все тесты
	docker-compose exec app pytest tests/ -v

test-cov: ## Запустить тесты с покрытием
	docker-compose exec app pytest tests/ --cov=app --cov-report=html --cov-report=term

test-watch: ## Запустить тесты в watch режиме
	docker-compose exec app ptw tests/ -- -v

# ==================== Code Quality ====================

lint: ## Проверить код с ruff
	docker-compose exec app ruff check app/

format: ## Отформатировать код с ruff
	docker-compose exec app ruff format app/

type-check: ## Проверить типы с mypy
	docker-compose exec app mypy app/

# ==================== Cleanup ====================

clean: ## Удалить контейнеры, volumes, images
	docker-compose down -v --rmi local

clean-all: ## Удалить ВСЁ включая volumes с данными БД
	docker-compose down -v --rmi all
	docker system prune -af --volumes

prune: ## Очистить неиспользуемые Docker ресурсы
	docker system prune -f

# ==================== Production-like ====================

prod: ## Запустить в production режиме
	docker-compose -f docker-compose.prod.yml up -d

prod-build: ## Собрать production образы
	docker-compose -f docker-compose.prod.yml build

prod-logs: ## Логи production
	docker-compose -f docker-compose.prod.yml logs -f

# ==================== Local Development (без Docker) ====================

install: ## Установить зависимости локально (venv)
	pip install -r requirements.txt

run-local: ## Запустить приложение локально (БД в Docker)
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

db-local: ## Поднять только БД и Redis в Docker
	docker-compose up -d postgres redis

# ==================== Utilities ====================

init: ## Первичная настройка проекта
	@echo "$(GREEN)Инициализация проекта...$(RESET)"
	docker-compose up -d postgres redis
	@sleep 3
	docker-compose up -d app
	@sleep 2
	$(MAKE) migrate
	@echo "$(GREEN)✓ Проект готов! API: http://localhost:8000/docs$(RESET)"

backup: ## Создать бэкап БД
	docker-compose exec postgres pg_dump -U postgres fitmetrics > backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)Бэкап создан!$(RESET)"

restore: ## Восстановить БД из бэкапа (использование: make restore file=backup.sql)
	docker-compose exec -T postgres psql -U postgres fitmetrics < $(file)
	@echo "$(GREEN)БД восстановлена!$(RESET)"

seed: ## Заполнить БД тестовыми данными
	docker-compose exec app python scripts/seed_db.py
	