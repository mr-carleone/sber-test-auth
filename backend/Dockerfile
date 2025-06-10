FROM python:3.10-slim

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV TZ="Europe/Moscow"

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование приложение
COPY ./app /app

# Запуск приложения
CMD ["sh", "-c", "uvicorn main:app --host ${APP_HOST} --port ${APP_PORT} --reload"]
