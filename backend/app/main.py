# app/main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, Response
from pathlib import Path
from core.config import settings
from core.logging import setup_logging
from core.middleware import setup_middleware
from core.storage import storage
# Импорт роутеров после инициализации логгера
from routes.auth_routes import router as auth_router, refresh_access_token, update_client_secret
from routes.statements_routes import router as statements_router

# Инициализация логирования
setup_logging()

logger = logging.getLogger(__name__)

# Проверка существования ключа
if settings.ENV.lower() != "dev":
    key_path = Path(settings.PRIVATE_KEY_PATH)
    if not key_path.exists():
        logger.critical(f"Private key not found at {key_path}")
        raise SystemExit(1)
    if not key_path.is_file():
        logger.critical(f"Private key path is not a file: {key_path}")
        raise SystemExit(1)

# Инициализация планировщика
scheduler = BackgroundScheduler() # type: ignore

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Запуск планировщика при старте
        scheduler.start() # type: ignore
        yield
    finally:
        # Остановка планировщика при завершении
        scheduler.shutdown() # type: ignore

# Создание приложения
app = FastAPI(
    title="Sber OAuth Service",
    debug=not settings.is_production,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan
)

# Настройка middleware
setup_middleware(app)

# Глобальный обработчик ошибок
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

app.include_router(auth_router, prefix="/api/v1")
app.include_router(statements_router, prefix="/api/v1")

# Проверка и обновление токена каждые 30 минут
@scheduler.scheduled_job('interval', minutes=30)  # type: ignore
def scheduled_token_refresh():
    if storage.refresh_token and storage.access_token_expired:
        import asyncio
        asyncio.run(refresh_access_token())

# Проверка client_secret каждые 12 часов
@scheduler.scheduled_job('interval', hours=12)  # type: ignore
def scheduled_secret_check():
    if storage.client_secret_expires_soon:
        logger.warning("Client secret expires soon, updating...")
        import asyncio
        asyncio.run(update_client_secret())

# Добавим middleware для автоматического обновления токена
@app.middleware("http")
async def auto_refresh_token(request: Request, call_next) -> Response: # type: ignore
    if storage.access_token_expired and storage.refresh_token:
        logger.warning("Access token expired, refreshing...")
        await refresh_access_token()

    response = await call_next(request) # type: ignore
    return response # type: ignore

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
