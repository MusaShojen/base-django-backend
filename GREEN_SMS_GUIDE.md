# 📱 Green SMS Integration Guide

Руководство по интеграции с Green SMS API через официальную библиотеку.

## 🚀 **Обновления в проекте**

### **✅ Что изменилось:**

1. **Официальная библиотека** - используем `greensms` вместо `requests`
2. **Улучшенная аутентификация** - логин/пароль вместо токена
3. **Отслеживание SMS** - сохранение `request_id` для мониторинга
4. **Статус доставки** - проверка статуса отправленных SMS
5. **Баланс аккаунта** - мониторинг баланса

## 🔧 **Настройка**

### **Переменные окружения:**

```bash
# .env файл
GREEN_SMS_USER=your-green-sms-user
GREEN_SMS_PASSWORD=your-green-sms-password
GREEN_SMS_DEBUG=True  # True для разработки, False для продакшена
```

### **Установка библиотеки:**

```bash
pip install greensms
```

## 📊 **Модель SMSVerification**

### **Новые поля:**

```python
class SMSVerification(models.Model):
    phone = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    request_id = models.CharField(max_length=100, blank=True, null=True)  # 🆕
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(verbose_name='Дата истечения')
```

### **Новые методы:**

```python
# Получение статуса SMS
sms_verification.get_sms_status()
# Возвращает: "delivered", "pending", "failed", "no_request_id"
```

## 🛠️ **Использование сервиса**

### **Базовое использование:**

```python
from authentication.services import GreenSMSService

# Инициализация сервиса
sms_service = GreenSMSService()

# Отправка SMS кода
sms_verification = sms_service.send_verification_code("+1234567890")

# Проверка кода
is_valid = sms_service.verify_code("+1234567890", "123456")
```

### **Отслеживание SMS:**

```python
# Получение статуса SMS
status = sms_service.get_sms_status("request_id_123")
print(status)  # "delivered", "pending", "failed"

# Проверка баланса
balance = sms_service.get_balance()
print(f"Баланс: {balance} руб.")
```

## 🔄 **Процесс отправки SMS**

### **1. Отправка кода:**

```python
# Пользователь запрашивает код
POST /api/auth/send-code/
{
    "phone": "+1234567890"
}

# Что происходит внутри:
# 1. Генерация 6-значного кода
# 2. Сохранение в БД с TTL 5 минут
# 3. Отправка через Green SMS API
# 4. Сохранение request_id для отслеживания
# 5. Возврат успешного ответа
```

### **2. Проверка кода:**

```python
# Пользователь вводит код
POST /api/auth/verify-code/
{
    "phone": "+1234567890",
    "code": "123456"
}

# Что происходит внутри:
# 1. Поиск кода в БД
# 2. Проверка срока действия
# 3. Проверка использования
# 4. Помечание как использованный
# 5. Возврат результата
```

## 🎯 **Debug режим**

### **В разработке:**

```python
# settings.py
GREEN_SMS_DEBUG = True

# Что происходит:
# - SMS не отправляются реально
# - Коды генерируются как обычно
# - В консоль выводится: "DEBUG SMS: +1234567890 - Ваш код: 123456"
# - request_id = "debug_request_id"
# - Статус всегда "delivered"
```

### **В продакшене:**

```python
# settings.py
GREEN_SMS_DEBUG = False

# Что происходит:
# - Реальная отправка через Green SMS API
# - Получение реального request_id
# - Проверка реального статуса доставки
```

## 📈 **Мониторинг и аналитика**

### **Отслеживание SMS:**

```python
# Получение всех SMS для номера
sms_verifications = SMSVerification.objects.filter(phone="+1234567890")

for sms in sms_verifications:
    print(f"Код: {sms.code}")
    print(f"Статус: {sms.get_sms_status()}")
    print(f"Request ID: {sms.request_id}")
    print(f"Создан: {sms.created_at}")
```

### **Статистика отправки:**

```python
# Количество отправленных SMS
total_sms = SMSVerification.objects.count()

# Количество доставленных
delivered_sms = SMSVerification.objects.filter(
    request_id__isnull=False
).count()

# Количество использованных кодов
used_codes = SMSVerification.objects.filter(is_used=True).count()
```

## 🔐 **Безопасность**

### **Rate Limiting:**

```python
# В views.py уже реализовано
if not RateLimiter.check_rate_limit(phone, limit=5, window=3600):
    return Response({'error': 'Превышен лимит запросов'})

# Ограничения:
# - 5 SMS в час на номер
# - 5 попыток ввода кода в час
# - Автоматическая блокировка при превышении
```

### **Валидация кодов:**

```python
# Проверки в verify_code:
# 1. Код существует в БД
# 2. Код не использован
# 3. Код не истек (5 минут)
# 4. Номер телефона совпадает
```

## 🚨 **Обработка ошибок**

### **Типы ошибок:**

```python
try:
    sms_verification = sms_service.send_verification_code(phone)
    if sms_verification:
        return Response({'message': 'Код отправлен'})
    else:
        return Response({'error': 'Ошибка отправки SMS'})
except Exception as e:
    return Response({'error': f'Ошибка сервиса: {str(e)}'})
```

### **Логирование:**

```python
# В debug режиме
print(f"DEBUG SMS: {phone} - {message}")

# В продакшене
logger.error(f"Ошибка отправки SMS: {e}")
```

## 📊 **API Endpoints**

### **Отправка кода:**

```http
POST /api/auth/send-code/
Content-Type: application/json

{
    "phone": "+1234567890"
}

# Ответ:
{
    "message": "Код подтверждения отправлен на ваш номер телефона",
    "phone": "+1234567890"
}
```

### **Проверка кода:**

```http
POST /api/auth/verify-code/
Content-Type: application/json

{
    "phone": "+1234567890",
    "code": "123456"
}

# Ответ:
{
    "message": "Код подтвержден успешно"
}
```

## 🔧 **Конфигурация Ansible**

### **Переменные для деплоя:**

```yaml
# group_vars/production.yml
green_sms_user: "your-production-user"
green_sms_password: "your-production-password"
green_sms_debug: false
```

### **Шаблон .env:**

```jinja2
# roles/django_app/templates/env.j2
GREEN_SMS_USER={{ green_sms_user }}
GREEN_SMS_PASSWORD={{ green_sms_password }}
GREEN_SMS_DEBUG={{ green_sms_debug | lower }}
```

## 📈 **Производительность**

### **Кэширование:**

```python
# SMS коды кэшируются в Redis
SMSVerificationCache.store_verification_code(phone, code)

# Rate limiting в Redis
RateLimiter.check_rate_limit(phone, limit=5, window=3600)
```

### **Оптимизация:**

- **Кэш кодов** - быстрый доступ к SMS кодам
- **Rate limiting** - защита от спама
- **Batch операции** - группировка запросов
- **Connection pooling** - переиспользование соединений

## 🆘 **Устранение проблем**

### **Проблема: SMS не отправляются**

```python
# Проверка настроек
print(f"User: {settings.GREEN_SMS_USER}")
print(f"Debug: {settings.GREEN_SMS_DEBUG}")

# Проверка баланса
balance = sms_service.get_balance()
print(f"Баланс: {balance}")

# Проверка статуса SMS
status = sms_service.get_sms_status(request_id)
print(f"Статус: {status}")
```

### **Проблема: Коды не работают**

```python
# Проверка в БД
sms = SMSVerification.objects.filter(phone=phone).last()
print(f"Код: {sms.code}")
print(f"Истек: {sms.is_expired()}")
print(f"Использован: {sms.is_used}")
```

## 📚 **Дополнительные ресурсы**

- [Green SMS API документация](https://docs.green-api.com/)
- [GreenSMS Python библиотека](https://pypi.org/project/greensms/)
- [Django Redis документация](https://github.com/jazzband/django-redis)

---

**Теперь ваш SMS сервис использует официальную библиотеку GreenSMS! 🚀**
