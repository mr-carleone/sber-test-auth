# Sber OAuth Service Backend

## Установка

### Разработка
```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
.\venv\Scripts\activate  # Windows

# Установка зависимостей для разработки
pip install -r requirements-dev.txt
```

### Продакшен
```bash
pip install -r requirements.txt
```

## Запуск

### Разработка
```bash
# Запуск с автоперезагрузкой
./scripts/run_dev.sh
```

### Продакшен
```bash
# Запуск с Gunicorn
./scripts/run_prod.sh
```

### Docker
```bash
# Сборка и запуск через docker-compose
docker-compose up --build
```

## Тестирование
```bash
pytest
```

## Линтинг
```bash
# Форматирование кода
black .
isort .

# Проверка типов
mypy .

# Проверка стиля
flake8
```
