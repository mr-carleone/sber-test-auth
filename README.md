# 🚀 Sber Auth Test For Development

![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-24.0.7-2496ED?logo=docker&logoColor=white)
![Uvicorn](https://img.shields.io/badge/Uvicorn-0.34-499848)

## 🚦 Быстрый старт

```bash
$ mkdir backend/configs
$ cp .env.template backend/configs/.env.dev
# Если нету сбер private_key.pem
$ openssl genpkey -algorithm RSA -out backend/app/private_key.pem -pkeyopt rsa_keygen_bits:2048
```

### Предварительные требования

- Docker 24.0+
- Docker Compose 2.20+

API будет доступно по адресу:
https://localhost

## 📚 Документация

После запуска проекта будет доступна:

- Swagger UI: [https://localhost/docs](https://localhost/docs)
- Redoc: [https://localhost/redoc](https://localhost/redoc)
- Healthcheck: [https://localhost/api/v1/health](https://localhost/api/v1/health)

## 📂 Структура проекта

```
sber-auth/
├── backend/
│   ├── app/
│   │   ├── core/             # Основные настройки
│   │   ├── routes/           # SQLAlchemy модели
│   │   ├── configs/          # Pydantic схемы
│   │   ├── private_key.pem   # sber key
│   │   └── main.py           # Точка входа
│   ├── Dockerfile            # Dockerfile
│   └── requirements.txt      # Зависимости
│
├── nginx/
│   ├── ssl/
│   │   ├── localhost.crt
│   │   └── localhost.key
│   ├── Dockerfile
│   └── nginx.conf
│
├── .env.template              # Шаблон переменных окружения
└── docker-compose.yml         # Docker Compose конфиг
```

## 🐳 Docker команды

```bash
# Запуск в фоновом режиме
$ docker-compose up -d

# Остановка контейнеров
$ docker-compose down

# Просмотр логов
$ docker-compose logs -f

# Пересборка образов
$ docker-compose build --no-cache
```

## Лицензия

MIT License © 2025 [Eruslanov Ivan]
