# src/core/logging.py
import logging
from colorlog import ColoredFormatter
from .config import get_settings

settings = get_settings()

def setup_logging():
    # Установка уровня логирования
    log_level = settings.LOG_LEVEL.upper()
    numeric_level = getattr(logging, log_level, logging.INFO)

    # Создание корневого логгера
    logger = logging.getLogger()
    logger.setLevel(numeric_level)

    # Форматирование в зависимости от среды
    if settings.ENV.lower() == "dev":
        formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s %(levelname)-8s %(name)s %(purple)s%(filename)s:%(lineno)d%(reset)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            reset=True,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
            secondary_log_colors={},
            style='%'
        )
    else:
        formatter = logging.Formatter(
            '{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", '
            '"file": "%(filename)s:%(lineno)d", "message": "%(message)s"}'
        )

    # Обработчик для вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Добавление обработчика к корневому логгеру
    logger.addHandler(console_handler)

    # Настройка логгеров Uvicorn
    for name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True

    logger.info(f"Logging configured for {settings.ENV} environment, level: {log_level}")
