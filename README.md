# ZavodHelper - База знаний производства

Веб-приложение для управления инцидентами и инструкциями на производстве.

## Технологии

- **Backend**: FastAPI (Python 3.11+)
- **Database**: SQLite с SQLAlchemy ORM
- **Frontend**: Jinja2 Templates + Vanilla JS
- **Validation**: Pydantic v2

## Структура проекта

```
ZavodHelper/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI приложение
│   ├── config.py         # Конфигурация
│   ├── database.py       # Подключение к БД
│   ├── models/           # SQLAlchemy модели
│   ├── schemas/          # Pydantic схемы
│   ├── crud/             # CRUD операции
│   ├── routers/          # API и HTML роуты
│   └── static/           # CSS, JS
├── templates/            # Jinja2 шаблоны
├── scripts/
│   └── init_db.py        # Инициализация БД
├── uploads/              # Загруженные файлы
├── requirements.txt
├── run.py                # Точка входа
├── Dockerfile
└── docker-compose.yml
```

## Быстрый старт

### Локальная установка

```bash
# Клонировать/перейти в директорию
cd ZavodHelper

# Создать виртуальное окружение
python -m venv venv

# Активировать (Windows)
venv\Scripts\activate

# Активировать (Linux/Mac)
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Инициализировать БД с демо-данными
python scripts/init_db.py

# Запустить сервер
python run.py
```

Приложение будет доступно по адресу: http://localhost:8000

### Docker

```bash
# Собрать и запустить
docker-compose up -d

# Или без docker-compose
docker build -t zavodhelper .
docker run -p 8000:8000 zavodhelper
```

## API Endpoints

### Основные

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/` | Главная страница (просмотр) |
| GET | `/editor` | Редактор |
| GET | `/health` | Проверка состояния |

### REST API

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/items` | Список всех элементов |
| GET | `/api/items/{id}` | Получить элемент |
| POST | `/api/items` | Создать элемент |
| PUT | `/api/items/{id}` | Обновить элемент |
| DELETE | `/api/items/{id}` | Удалить элемент |
| GET | `/api/items/search?q=` | Поиск |
| GET | `/api/incidents` | Все инциденты |
| GET | `/api/instructions` | Все инструкции |
| GET | `/api/export` | Экспорт в JSON |
| POST | `/api/import` | Импорт из JSON |

## Конфигурация

Через переменные окружения:

```bash
HOST=0.0.0.0          # Хост сервера
PORT=8000             # Порт
DEBUG=true            # Режим отладки
DATABASE_URL=sqlite:///./zavod.db  # URL базы данных
```

## Масштабирование

### Миграция на PostgreSQL

1. Установить драйвер:
```bash
pip install psycopg2-binary
```

2. Изменить `DATABASE_URL`:
```bash
DATABASE_URL=postgresql://user:pass@localhost/zavodhelper
```

3. Убрать `check_same_thread` из `database.py`

### Добавление аутентификации

Рекомендуется использовать `fastapi-users` или JWT токены.

### Кэширование

Для высоких нагрузок добавить Redis:
```bash
pip install redis aioredis
```

## Разработка

### Добавление новых моделей

1. Создать модель в `app/models/models.py`
2. Создать схемы в `app/schemas/schemas.py`
3. Добавить CRUD операции в `app/crud/crud.py`
4. Создать роутер в `app/routers/`
5. Подключить роутер в `app/main.py`

### Тестирование

```bash
pip install pytest pytest-asyncio httpx
pytest tests/
```

## Лицензия

MIT
