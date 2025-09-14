# Books API

API разработанный на основе FastAPI, для управления книгами, отзывами и пользователями

## Особенности
- **Взаимодействие с книгами** — CRUD операции для книг
- **Система отзывов** — пользователи могут делать обзоры на книги с рейтингом
- **Пользовательские профили** — полное управление пользователями
- **JWT-аутентификация** — безопасный логин и регистрация
- **Поддержка PostgreSQL** — СУБД, готовая для продакшена
- **Асинхронная архитектура** — высокая производительность с использованием async/await

## Установка
### 1. Клонируйте репозиторий
```bash
git clone https://github.com/newyearoldme/books-api.git
cd books-api
```

### 2. Установите зависимости
```bash
poetry install
```
или
```bash
pip install -r requirements.txt
```

### 3. Настройте .env файл (как пример — .env.example)
```bash
cp .env.example .env
```

### 3.5 Создание секретного ключа для .env
```bash
poetry run python scripts/generate_secret.py
```
или
```bash
python scripts/generate_secret.py
```

### 4. Создайте таблицы в базе данных
```bash
poetry run python scripts/init_db.py
```
или
```bash
python scripts/init_db.py
```

### 5. Запуск приложения
```bash
poetry run python run.py
```
```bash
poetry run uvicorn src.main:app --reload
```
или
```bash
python run.py
```
```bash
uvicorn src.main:app --reload
```

## Эндпоинты
### Auth
- `POST /auth/login` — аутентификация пользователя

### Books
- `POST /books/` — создание новой книги
- `GET /books/` — получение всех книг
- `GET /books/{book_id}` — получение конкретной книги по ID
- `GET /books/top_rated` — получение наиболее популярной книги по рейтингу
- `PUT /books/{book_id}` — обновление данных книги
- `DELETE /books/{book_id}` — удаление книги

### Review
- `POST /reviews/` — создание отзыва к книге
- `GET /reviews/` — получение всех отзывов
- `GET /reviews/book/{book_id}/` — получение отзывов конкретной книги по ID
- `GET /reviews/user/{user_id}/` — получение отзывов конкретного пользователя по ID
- `GET /reviews/{review_id}/` — получение отзыва
- `DELETE /reviews/{review_id}/` — удаление отзыва
- `PUT /reviews/{review_id}/` — обновление отзыва
- `GET /reviews/{book_id}/average_rating` — получение среднего рейтинга книги

### Users
- `POST /users/` — регистрация нового пользователя
- `GET /users/me/` — получение текущего пользователя
- `GET /users/` — список всех пользователей
- `GET /users/{user_id}/` — получение пользователя по ID
- `GET /users/by_email/{email}/` — получение пользователя по электронной почте
- `GET /users/by_username/{username}/` — получение пользователя по имени
- `PUT /users/{user_id}/` — обновление данных пользователя
- `DELETE /users/{user_id}/` — удаление пользователя по ID

## Тесты
Тесты покрывают все основные CRUD операции. Запуск происходит через
```bash
poetry run pytest -v
```
или
```bash
pytest -v
```
