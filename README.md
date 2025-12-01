# E-Commerce API Server

Полнофункциональный API сервер интернет-магазина, построенный на FastAPI и PostgreSQL, с управлением товарами, корзиной, заказами и отзывами, а также безопасной JWT аутентификацией.

## Возможности

- JWT аутентификация
- FastAPI веб-фреймворк
- PostgreSQL с SQLAlchemy ORM
- Миграции базы данных с Alembic
- Полная функциональность интернет-магазина (товары, корзина, заказы, отзывы)
- RESTful API с полным набором CRUD операций
- Разделение прав доступа (администраторы и пользователи)
- Пагинация для всех списков
- Поиск и фильтрация товаров
- Docker и Docker Compose поддержка

## Быстрый старт

```bash
docker compose up --build

docker compose exec web alembic upgrade head
docker compose exec web python scripts/seed_data.py
```

Приложение будет доступно на `https://localhost:8000/docs`

## Установка

### 1. Клонируйте репозиторий

```bash
git clone <url-репозитория>
cd <название-директории>
```

### 2. Настройте переменные окружения

Создайте файл `.env` в корне проекта:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=myapp
DB_ECHO=False

# Первый администратор (создается при старте, если нет администраторов)
FIRST_ADMIN_EMAIL=admin@example.com
FIRST_ADMIN_PASSWORD=secure_password_123
FIRST_ADMIN_NAME=Главный Администратор

# CORS настройки (разделенные запятыми)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Безопасность
SECRET_KEY=your-secret-key-change-this-in-production-please-make-it-secure
```

### 3. Запуск

**С Docker (рекомендуется):**
```bash
docker compose up --build
docker compose exec web alembic upgrade head
```

**Локально:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn app.main:app --reload
```

## API Эндпоинты

### Аутентификация
- `POST /auth/register` - Регистрация
- `POST /auth/login` - Вход
- `GET /auth/me` - Текущий пользователь

### Пользователи
- `GET /users/me` - Мой профиль
- `PUT /users/me` - Обновить профиль
- `POST /users/me/change-password` - Изменить пароль
- `GET /users` - Список пользователей (админы)
- `PUT /users/{user_id}` - Обновить пользователя (админы)

### Категории
- `GET /categories/` - Список категорий
- `GET /categories/{id}` - Категория
- `POST /categories/` - Создать (админы)
- `PUT /categories/{id}` - Обновить (админы)
- `DELETE /categories/{id}` - Удалить (админы)

### Товары
- `GET /products/` - Список товаров (с фильтрами: `category_id`, `search`, `min_price`, `max_price`, `in_stock`)
- `GET /products/{id}` - Товар
- `POST /products/` - Создать (админы)
- `PUT /products/{id}` - Обновить (админы)
- `DELETE /products/{id}` - Удалить (админы)

### Корзина
- `GET /cart` - Моя корзина
- `POST /cart/items` - Добавить товар
- `PUT /cart/items/{id}` - Обновить количество
- `DELETE /cart/items/{id}` - Удалить товар
- `DELETE /cart` - Очистить корзину

### Заказы
- `GET /orders` - Мои заказы
- `GET /orders/{id}` - Заказ
- `POST /orders` - Создать заказ из корзины
- `PUT /orders/{id}` - Обновить статус

### Отзывы
- `GET /reviews/product/{product_id}` - Отзывы на товар
- `GET /reviews/my` - Мои отзывы
- `POST /reviews` - Создать отзыв
- `PUT /reviews/{id}` - Обновить отзыв
- `DELETE /reviews/{id}` - Удалить отзыв

Все списки поддерживают пагинацию: `?page=1&page_size=20`

## Тестовые учетные данные

После выполнения `python scripts/seed_data.py`:

- `ivan@example.com` / `password123` (Администратор)
- `maria@example.com` / `password123`
- `alexey@example.com` / `password123`

## Миграции

```bash
alembic revision --autogenerate -m "Описание изменений"
alembic upgrade head

docker-compose exec web alembic revision --autogenerate -m "Описание"
docker-compose exec web alembic upgrade head
```

## Структура проекта

```
.
├── app/              # Основной пакет приложения
│   ├── main.py       # FastAPI приложение и маршруты
│   ├── config.py     # Конфигурация
│   ├── database.py   # Подключение к БД
│   ├── auth.py       # Аутентификация
│   ├── models/       # Модели БД
│   ├── schemas/      # Pydantic схемы
│   └── routers/      # API роутеры
├── scripts/          # Утилитарные скрипты
├── tests/            # Тесты
├── alembic/          # Миграции БД
└── frontend/         # React фронтенд
```

## Тестирование

```bash
# all test start
pytest

# with coverage
pytest --cov=app
```

## Развертывание

1. Установите безопасные переменные окружения
2. Используйте `docker-compose.prod.yml` для production окружения
3. Настройте резервное копирование БД
4. Включите HTTPS
