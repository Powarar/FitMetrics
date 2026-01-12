.PHONY: help build up down restart logs shell test migrate makemigrations clean dev prod

# Цвета для вывода
YELLOW := \033[1;33m
GREEN := \033[1;32m
RESET := \033[0m

# По умолчанию показываем help
.DEFAULT_GOAL := help

help:
	@echo "$(GREEN)Доступные команды:$(RESET)"
	@echo "  $(YELLOW)build$(RESET)          Собрать Docker образы"
	@echo "  $(YELLOW)up$(RESET)             Поднять все сервисы в фоне"
	@echo "  $(YELLOW)down$(RESET)           Остановить и удалить контейнеры"
	@echo "  $(YELLOW)dev$(RESET)            Запустить в dev режиме (с rebuild)"
	@echo "  $(YELLOW)shell$(RESET)          Открыть bash в контейнере api"
	@echo "  $(YELLOW)migrate$(RESET)        Применить миграции Alembic"
	@echo "  $(YELLOW)test$(RESET)           Запустить все тесты"
	@echo "  $(YELLOW)lint$(RESET)           Проверить код ruff"
	@echo "  $(YELLOW)type-check$(RESET)     Проверить типы mypy"
	@echo "  $(YELLOW)clean$(RESET)          Удалить контейнеры/volumes/images"


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

logs-api: ## Показать логи только приложения
	docker-compose logs -f api

ps: ## Показать статус контейнеров
	docker-compose ps

# ==================== Development ====================

dev: ## Запустить в dev режиме (с rebuild)
	docker-compose up --build

shell: ## Открыть bash в контейнере api
	docker-compose exec api bash

shell-db: ## Открыть psql в Postgres
	docker-compose exec postgres psql -U postgres -d fitmetrics

python: ## Открыть Python REPL в контейнере
	docker-compose exec api python

# ==================== Database ====================

psql: ## Открыть psql в контейнере
	docker compose exec postgres psql -U sportuser -d sportdb

migrate: ## Применить миграции Alembic
	docker-compose exec api alembic upgrade head

makemigrations: ## Создать новую миграцию (использование: make makemigrations m="описание")
	docker-compose exec api alembic revision --autogenerate -m "$(m)"

downgrade: ## Откатить последнюю миграцию
	docker-compose exec api alembic downgrade -1

db-reset: ## Пересоздать БД (УДАЛИТ ВСЕ ДАННЫЕ!)
	docker-compose down -v
	docker-compose up -d postgres redis
	@echo "$(YELLOW)Ждём запуска Postgres...$(RESET)"
	@sleep 3
	docker-compose up -d api
	$(MAKE) migrate

# ==================== Testing ====================

test: ## Запустить все тесты
	docker-compose exec api pytest tests/ -v

test-cov: ## Запустить тесты с покрытием
	docker-compose exec api pytest tests/ --cov=api --cov-report=html --cov-report=term

test-watch: ## Запустить тесты в watch режиме
	docker-compose exec api ptw tests/ -- -v

# ==================== Code Quality ====================

lint: ## Проверить код с ruff
	docker-compose exec api ruff check api/

format: ## Отформатировать код с ruff
	docker-compose exec api ruff format api/

type-check: ## Проверить типы с mypy
	docker-compose exec api mypy api/

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
	docker-compose up -d api
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
	docker-compose exec api python scripts/seed_db.py
	