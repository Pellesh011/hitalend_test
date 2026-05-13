
- Docker & Docker Compose
- Python 3.9

# Установка и создание таблиц в бд

Необходимо создать файл .env c DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/app_db

```bash
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

docker compose up -d postgres

alembic revision --autogenerate -m "init"
alembic upgrade head
```
## Запуск проекта 

```bash 
docker compose up -d --build
```

## swagger

http://localhost:8000/docs

## Тесты 

```bash
pytest
```