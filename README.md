
- Docker & Docker Compose
- Python 3.9

# Установка и создание таблиц в бд

Необходимо создать файл .env c DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/app_db

```bash
python3.9 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

docker compose up -d postgres

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
pip install -r requirements-dev.txt
pytest
```

## lint


```bash
pip install -r requirements-dev.txt
black .
ruff check . --fix
```