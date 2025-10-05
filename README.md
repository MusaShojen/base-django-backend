# Django Backend с аутентификацией и ролями

Базовый Django backend с системой аутентификации через SMS, ролями пользователей и Swagger документацией.

## Возможности

- 🔐 **Аутентификация через SMS** с интеграцией Green SMS API
- 👥 **Система ролей**: пользователь, администратор, суперадминистратор
- 🛡️ **Защита роутов** с проверкой ролей
- 📚 **Swagger документация** для всех API endpoints
- 🗄️ **База данных**: PostgreSQL для продакшена, SQLite для разработки
- 🔧 **Режим отладки** для SMS сервиса

## Установка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd base-python-back
```

### 2. Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

Скопируйте файл `env.example` в `.env` и настройте переменные:

```bash
cp env.example .env
```

Отредактируйте `.env` файл:

```env
# Django settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database settings
DATABASE_URL=sqlite:///db.sqlite3

# Green SMS API settings
GREEN_SMS_API_URL=https://api.green-api.com
GREEN_SMS_API_TOKEN=your-green-sms-token
GREEN_SMS_DEBUG=True
```

### 5. Выполнение миграций

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Создание суперпользователя

```bash
python manage.py createsuperuser
```

### 7. Запуск сервера

```bash
python manage.py runserver
```

## API Endpoints

### Аутентификация

- `POST /api/auth/send-code/` - Отправка SMS кода
- `POST /api/auth/verify-code/` - Проверка SMS кода
- `POST /api/auth/register/` - Регистрация пользователя
- `POST /api/auth/login/` - Вход в систему
- `POST /api/auth/logout/` - Выход из системы

### Профиль пользователя

- `GET /api/auth/profile/` - Получение профиля
- `PUT /api/auth/profile/update/` - Обновление профиля

### Защищенные роуты

- `GET /api/auth/dashboard/` - Дашборд для всех пользователей
- `GET /api/auth/admin/` - Панель администратора
- `GET /api/auth/superadmin/` - Панель суперадминистратора

### Управление пользователями (только для админов)

- `GET /api/users/` - Список пользователей
- `GET /api/users/{id}/` - Детали пользователя
- `PUT /api/users/{id}/role/` - Изменение роли
- `DELETE /api/users/{id}/delete/` - Удаление пользователя
- `GET /api/users/stats/` - Статистика пользователей

## Swagger документация

После запуска сервера документация доступна по адресам:

- **Swagger UI**: http://localhost:8000/swagger/
- **JSON Schema**: http://localhost:8000/swagger.json

### Особенности документации

- 📝 **Подробные описания** для каждого endpoint
- 🔍 **Примеры запросов и ответов** для всех статус кодов
- 🛡️ **Информация о правах доступа** для каждого роута
- 🧪 **Интерактивное тестирование** API прямо в браузере
- 📊 **Примеры данных** для успешных и ошибочных ответов

📖 **Подробное руководство**: [API_GUIDE.md](API_GUIDE.md) - полное руководство по использованию API с примерами запросов

## Система ролей

### Роли пользователей

1. **user** - Обычный пользователь
2. **admin** - Администратор
3. **superadmin** - Суперадминистратор

### Декораторы для защиты роутов

```python
from authentication.decorators import require_roles, require_admin, require_superadmin

# Только для определенных ролей
@require_roles('admin', 'superadmin')
def admin_view(request):
    pass

# Только для администраторов
@require_admin
def admin_panel(request):
    pass

# Только для суперадминистраторов
@require_superadmin
def superadmin_panel(request):
    pass
```

## Green SMS API

### Режим отладки

В режиме отладки (`GREEN_SMS_DEBUG=True`) SMS не отправляются, а в консоль выводится сообщение:

```
DEBUG SMS: +1234567890 - Ваш код подтверждения: 123456
```

### Продакшен режим

Для продакшена установите:

```env
GREEN_SMS_DEBUG=False
GREEN_SMS_API_TOKEN=your-real-token
```

## База данных

### Разработка (SQLite)

По умолчанию используется SQLite для разработки:

```env
DATABASE_URL=sqlite:///db.sqlite3
```

### Продакшен (PostgreSQL)

Для продакшена используйте PostgreSQL:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

## Структура проекта

```
base-python-back/
├── backend/                 # Основные настройки Django
│   ├── settings.py         # Настройки проекта
│   ├── urls.py             # Основные URL маршруты
│   └── wsgi.py
├── authentication/         # Приложение аутентификации
│   ├── models.py          # Модели для SMS и токенов
│   ├── views.py           # API endpoints
│   ├── serializers.py     # Сериализаторы
│   ├── services.py        # Сервис Green SMS
│   ├── decorators.py      # Декораторы для ролей
│   └── urls.py            # URL маршруты
├── users/                  # Приложение пользователей
│   ├── models.py          # Модель пользователя
│   ├── views.py           # Управление пользователями
│   └── urls.py            # URL маршруты
├── requirements.txt        # Зависимости Python
├── .env.example           # Пример переменных окружения
├── .gitignore             # Git ignore файл
└── README.md              # Документация
```

## Развертывание

### Heroku

1. Создайте файл `Procfile`:

```
web: gunicorn backend.wsgi --log-file -
```

2. Установите переменные окружения в Heroku:

```bash
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DATABASE_URL=postgresql://...
```

### Docker

Создайте `Dockerfile`:

```dockerfile
FROM python:3.11

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## Лицензия

MIT License
