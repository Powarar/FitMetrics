
<div align="center">

# 💪 FitMetrics

**Современный бэкенд для фитнес-трекинга на FastAPI**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Описание](#-описание) •
[Возможности](#-возможности) •
[Установка](#-установка) •
[Использование](#-использование) •
[API](#-api-документация) •
[Архитектура](#-архитектура)

</div>

---

## 📋 Описание

FitMetrics — это REST API для управления тренировками, отслеживания прогресса и аналитики в фитнесе. Построен с использованием современных production-ready паттернов и асинхронной архитектуры.

### ✨ Возможности

- 🏋️ **Управление тренировками** — создание, просмотр, обновление записей о тренировках
- 📊 **Аналитика прогресса** — отслеживание объёма, максимальных весов, личных рекордов
- 💾 **Гибкая структура** — поддержка различных упражнений и мышечных групп
- 🔐 **JWT Аутентификация** — безопасный доступ к персональным данным
- 🚀 **Асинхронность** — высокая производительность благодаря async/await
- 📦 **Docker Ready** — быстрый запуск в любом окружении
- 🧪 **Тестируемость** — покрытие тестами и CI/CD интеграция

---

## 🛠 Технологический стек

| Категория | Технологии |
|-----------|-----------|
| **Backend** | FastAPI, Python 3.11+, Pydantic |
| **База данных** | PostgreSQL, SQLAlchemy 2.0 (async) |
| **Кэширование** | Redis |
| **Миграции** | Alembic |
| **Контейнеризация** | Docker, Docker Compose |
| **Оркестрация** | Apache Airflow (планирование задач) |
| **Тестирование** | pytest, pytest-asyncio |

---

## 🚀 Установка

### Требования

- Docker & Docker Compose
- Make (опционально, для удобства)

### Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone https://github.com/Powarar/FitMetrics.git
cd FitMetrics

# 2. Создать .env файл
cp .env.example .env

# 3. Запустить проект (с Make)
make init

# ИЛИ без Make
docker-compose up -d
docker-compose exec app alembic upgrade head
```

🎉 **Готово!** API доступен на http://localhost:8000

---

## 📖 Использование

### Основные команды

```bash
# Поднять все сервисы
make up

# Просмотр логов
make logs-app

# Применить миграции
make migrate

# Создать новую миграцию
make makemigrations m="описание изменения"

# Запустить тесты
make test

# Зайти в контейнер
make shell

# Остановить все сервисы
make down

# Показать все команды
make help
```


### Локальная разработка (без Docker для кода)

```bash
# 1. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Поднять только БД и Redis в Docker
make db-local

# 4. Применить миграции
alembic upgrade head

# 5. Запустить приложение
uvicorn app.main:app --reload
```


---

## 📚 API Документация

После запуска проекта доступны:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI схема**: http://localhost:8000/openapi.json


### Примеры запросов

#### Создать тренировку

```bash
curl -X POST "http://localhost:8000/api/v1/workouts" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "user_id": 1,
    "exercise_name": "Bench Press",
    "muscle_group": "Chest",
    "sets": 4,
    "reps": 10,
    "weight": 80.5
  }'
```


#### Получить статистику

```bash
curl -X GET "http://localhost:8000/api/v1/metrics/user/1?period=30" \
  -H "Authorization: Bearer YOUR_TOKEN"
```


#### Список всех тренировок

```bash
curl -X GET "http://localhost:8000/api/v1/workouts?user_id=1&limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```


---

## 🏗 Архитектура

Проект построен на **Repository Pattern + Service Layer** с чистой архитектурой:

```
app/
├── api/
│   └── v1/
│       ├── workouts.py      # Endpoints для тренировок
│       └── metrics.py       # Endpoints для аналитики
├── core/
│   ├── config.py            # Настройки приложения
│   └── security.py          # JWT, хеширование паролей
├── db/
│   ├── database.py          # SQLAlchemy engine, сессии
│   └── base.py              # Базовые модели
├── models/
│   ├── workout.py           # ORM модель Workout
│   └── exercise.py          # ORM модель Exercise
├── repositories/
│   └── workout_repo.py      # Работа с БД (CRUD)
├── schemas/
│   └── workout.py           # Pydantic схемы (валидация)
├── services/
│   └── workout_service.py   # Бизнес-логика
└── main.py                  # FastAPI приложение
```


### Принципы

- ✅ **Dependency Injection** — управление зависимостями через FastAPI
- ✅ **Repository Pattern** — изоляция логики работы с БД
- ✅ **Service Layer** — бизнес-логика отдельно от endpoints
- ✅ **Async/Await** — асинхронная работа с базой данных
- ✅ **Type Hints** — строгая типизация для надёжности
- ✅ **SOLID** — чистая архитектура и разделение ответственности

---

## 🧪 Тестирование

```bash
# Запустить все тесты
make test

# С покрытием кода
make test-cov

# Конкретный тест
docker-compose exec app pytest tests/test_workouts.py -v

# Watch режим (автоматический перезапуск)
make test-watch
```

Структура тестов:

```
tests/
├── conftest.py              # Фикстуры pytest
├── test_workouts.py         # Тесты API тренировок
├── test_metrics.py          # Тесты аналитики
└── test_repositories.py     # Тесты репозиториев
```


---

## 🗃 База данных

### Схема

```sql
-- Упражнения
CREATE TABLE exercises (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    muscle_group VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Тренировки
CREATE TABLE workouts (
    id UUID PRIMARY KEY,
    user_id INTEGER NOT NULL,
    exercise_id UUID REFERENCES exercises(id),
    sets INTEGER NOT NULL,
    reps INTEGER NOT NULL,
    weight FLOAT NOT NULL,
    total_volume FLOAT NOT NULL,
    workout_date TIMESTAMP DEFAULT NOW()
);
```


### Миграции

```bash
# Создать новую миграцию
make makemigrations m="add indexes to workouts"

# Применить
make migrate

# Откатить последнюю
make downgrade

# Полный сброс БД (ОСТОРОЖНО!)
make db-reset
```


---

## 🔐 Безопасность

- 🔒 **JWT токены** — stateless аутентификация
- 🛡️ **Bcrypt** — безопасное хеширование паролей
- 🚫 **Redis blacklist** — отзыв токенов при logout
- ⏱️ **Rate limiting** — защита от брутфорса
- 🔍 **SQL Injection защита** — параметризованные запросы SQLAlchemy

---

## 📊 Переменные окружения

Создай `.env` файл в корне проекта:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/fitmetrics

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
DEBUG=True
API_V1_PREFIX=/api/v1
```


---

## 🚢 Deployment

### Production с Docker Compose

```bash
# Собрать production образы
make prod-build

# Запустить в production режиме
make prod

# Логи
make prod-logs
```


### Рекомендации для production

- [ ] Использовать `.env` с секретами (не коммитить!)
- [ ] Настроить Nginx reverse proxy
- [ ] Включить HTTPS (Let's Encrypt)
- [ ] Добавить логирование (structlog + ELK)
- [ ] Настроить мониторинг (Prometheus + Grafana)
- [ ] Использовать managed БД (AWS RDS, Yandex Cloud)
- [ ] Настроить бэкапы БД (ежедневные, автоматические)
- [ ] Rate limiting через nginx/cloudflare

---

## 🤝 Вклад в проект

Приветствуются Pull Request'ы! Перед отправкой:

1. Создай новую ветку (`git checkout -b feature/amazing-feature`)
2. Commit изменения (`git commit -m 'Add amazing feature'`)
3. Push в ветку (`git push origin feature/amazing-feature`)
4. Открой Pull Request

### Coding Style

```bash
# Форматирование кода
make format

# Проверка линтером
make lint

# Проверка типов
make type-check
```

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. [LICENSE](LICENSE) для деталей.

---

## 👨‍💻 Автор

**Powarar**

- GitHub: [@Powarar](https://github.com/Powarar)
- Telegram: [@safonovpavel](https://t.me/@safonovpavel)

---

## ⭐ Поддержка

Если проект был полезен — поставь звёздочку! ⭐

Нашёл баг? [Создай issue](https://github.com/Powarar/FitMetrics/issues)

---

<div align="center">



[⬆ Вернуться к началу](#-fitmetrics)