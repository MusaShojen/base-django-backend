# Руководство по использованию API

## Быстрый старт

### 1. Регистрация пользователя

```bash
# 1. Отправить SMS код
curl -X POST http://localhost:8000/api/auth/send-code/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890"}'

# 2. Проверить код (в режиме дебага всегда 123456)
curl -X POST http://localhost:8000/api/auth/verify-code/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890", "code": "123456"}'

# 3. Зарегистрироваться
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+1234567890",
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "password123",
    "password_confirm": "password123"
  }'
```

### 2. Вход в систему

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+1234567890",
    "password": "password123"
  }'
```

### 3. Использование токена

```bash
# Получить профиль
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"

# Дашборд пользователя
curl -X GET http://localhost:8000/api/auth/dashboard/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

## Аутентификация

### Типы аутентификации

1. **SMS аутентификация** - для регистрации и подтверждения номера
2. **Token аутентификация** - для API запросов
3. **Ролевая аутентификация** - для доступа к защищенным роутам

### Получение токена

После успешного входа или регистрации вы получите токен:

```json
{
  "message": "Вход выполнен успешно",
  "user": { ... },
  "token": "12345678-1234-1234-1234-123456789abc"
}
```

### Использование токена

Добавьте токен в заголовок Authorization:

```
Authorization: Token 12345678-1234-1234-1234-123456789abc
```

## Роли и права доступа

### Роли пользователей

| Роль | Описание | Доступные роуты |
|------|----------|-----------------|
| `user` | Обычный пользователь | `/dashboard/`, `/profile/` |
| `admin` | Администратор | Все роуты пользователя + `/admin/`, `/users/` |
| `superadmin` | Суперадминистратор | Все роуты + `/superadmin/`, удаление пользователей |

### Примеры запросов по ролям

#### Для обычного пользователя

```bash
# Дашборд
curl -X GET http://localhost:8000/api/auth/dashboard/ \
  -H "Authorization: Token YOUR_TOKEN"

# Профиль
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Token YOUR_TOKEN"
```

#### Для администратора

```bash
# Список пользователей
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Token ADMIN_TOKEN"

# Изменить роль пользователя
curl -X PUT http://localhost:8000/api/users/1/role/ \
  -H "Authorization: Token ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role": "admin"}'

# Статистика пользователей
curl -X GET http://localhost:8000/api/users/stats/ \
  -H "Authorization: Token ADMIN_TOKEN"
```

#### Для суперадминистратора

```bash
# Удалить пользователя
curl -X DELETE http://localhost:8000/api/users/1/delete/ \
  -H "Authorization: Token SUPERADMIN_TOKEN"

# Панель суперадминистратора
curl -X GET http://localhost:8000/api/auth/superadmin/ \
  -H "Authorization: Token SUPERADMIN_TOKEN"
```

## Коды ответов

### Успешные ответы

- `200 OK` - Успешный запрос
- `201 Created` - Ресурс создан

### Ошибки клиента

- `400 Bad Request` - Неверные данные запроса
- `401 Unauthorized` - Требуется аутентификация
- `403 Forbidden` - Недостаточно прав доступа
- `404 Not Found` - Ресурс не найден

### Ошибки сервера

- `500 Internal Server Error` - Внутренняя ошибка сервера

## Примеры ошибок

### Ошибка аутентификации

```json
{
  "error": "Требуется аутентификация"
}
```

### Недостаточно прав

```json
{
  "error": "Недостаточно прав доступа"
}
```

### Ошибка валидации

```json
{
  "phone": ["Номер телефона должен начинаться с '+'"],
  "password": ["Пароли не совпадают"]
}
```

## Тестирование в Swagger UI

1. Откройте http://localhost:8000/swagger/
2. Найдите нужный endpoint
3. Нажмите "Try it out"
4. Заполните параметры
5. Нажмите "Execute"

### Авторизация в Swagger

1. Нажмите кнопку "Authorize" в правом верхнем углу
2. Введите токен в формате: `Token YOUR_TOKEN_HERE`
3. Нажмите "Authorize"
4. Теперь вы можете тестировать защищенные роуты

## Отладка

### Режим отладки SMS

В файле `.env` установите:

```env
GREEN_SMS_DEBUG=True
```

В этом режиме:
- SMS не отправляются реально
- Всегда используется код `123456`
- Сообщения выводятся в консоль

### Логи сервера

Сервер выводит подробные логи всех запросов:

```
[05/Oct/2025 08:06:09] "GET /swagger/ HTTP/1.1" 200 2221
[05/Oct/2025 08:06:10] "POST /api/auth/login/ HTTP/1.1" 200 1234
```

## Полезные команды

### Создание суперадминистратора

```bash
python manage.py shell
```

```python
from users.models import User
User.objects.create_superuser(
    phone='+1234567890',
    username='admin',
    email='admin@example.com',
    password='admin123',
    role='superadmin'
)
```

### Проверка пользователей

```bash
python manage.py shell
```

```python
from users.models import User
users = User.objects.all()
for user in users:
    print(f"{user.phone} - {user.role}")
```
