# app/main.py
import time
from fastapi import FastAPI, Request
from pathlib import Path
from core.config import settings
from core.logging import setup_logging
from apscheduler.schedulers.background import BackgroundScheduler
from core.storage import storage
# Импорт роутеров после инициализации логгера
from routes.auth_routes import router as auth_router, refresh_access_token, update_client_secret
from routes.statements_routes import router as statements_router

# Инициализация логирования
setup_logging()

# Проверка существования ключа
if settings.ENV.lower() != "dev":
    key_path = Path(settings.PRIVATE_KEY_PATH)
    if not key_path.exists():
        logger.critical(f"Private key not found at {key_path}")
        raise SystemExit(1)
    if not key_path.is_file():
        logger.critical(f"Private key path is not a file: {key_path}")
        raise SystemExit(1)

# Создание приложения
app = FastAPI(
    title="Sber OAuth Service",
    debug=not settings.is_production,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(statements_router, prefix="/api/v1")

# Инициализация планировщика
scheduler = BackgroundScheduler()

# Проверка и обновление токена каждые 30 минут
@scheduler.scheduled_job('interval', minutes=30)
def scheduled_token_refresh():
    if storage.refresh_token and storage.access_token_expired:
        # Для асинхронных функций используем asyncio.run в синхронном контексте
        import asyncio
        asyncio.run(refresh_access_token())

# Проверка client_secret каждые 12 часов
@scheduler.scheduled_job('interval', hours=12)
def scheduled_secret_check():
    if storage.client_secret_expires_soon:
        logger.warning("Client secret expires soon, updating...")
        import asyncio
        asyncio.run(update_client_secret())

scheduler.start()

# Остановка планировщика при завершении
@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

# Добавим middleware для автоматического обновления токена
@app.middleware("http")
async def auto_refresh_token(request: Request, call_next):
    # Если токен просрочен и есть refresh_token
    if storage.access_token_expired and storage.refresh_token:
        logger.warning("Access token expired, refreshing...")
        await refresh_access_token()

    response = await call_next(request)
    return response

@app.get("/api/v1/")
async def root():
    return {"message": "Sber OAuth Service", "environment": settings.ENV}

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "OK",
        "token_expired": storage.access_token_expired,
        "secret_expires_soon": storage.client_secret_expires_soon
    }
