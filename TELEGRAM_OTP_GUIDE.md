# 📱 Telegram OTP Integration Guide

Руководство по интеграции Telegram OTP Gateway API в Django проект.

## 🚀 **Обзор интеграции**

### **✅ Что добавлено:**

1. **Telegram Gateway API** - официальная интеграция с Telegram OTP
2. **Универсальный OTP сервис** - выбор между Telegram и SMS
3. **Автоматический fallback** - SMS как резервный вариант
4. **Проверка доступности** - определение возможности отправки в Telegram
5. **Мониторинг статуса** - отслеживание доставки кодов

## 🔧 **Настройка**

### **Переменные окружения:**

```bash
# .env файл
TELEGRAM_GATEWAY_ENABLED=True
TELEGRAM_GATEWAY_TOKEN=your-telegram-gateway-token
TELEGRAM_GATEWAY_DEBUG=True  # True для разработки, False для продакшена
```

### **Получение токена:**

1. Зайдите в [Telegram Gateway](https://gatewayapi.telegram.org/)
2. Создайте аккаунт
3. Получите access token в настройках
4. Добавьте токен в переменные окружения

## 📊 **Архитектура системы**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Пользователь  │───▶│  Universal OTP  │───▶│   Telegram API  │
│   (Frontend)    │    │     Service     │    │   (Primary)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Green SMS     │
                       │   (Fallback)    │
                       └─────────────────┘
```

## 🎯 **Логика работы**

### **1. Отправка кода:**

```python
# Пользователь запрашивает код
POST /api/auth/send-code/
{
    "phone": "+1234567890",
    "prefer_telegram": true  # опционально, по умолчанию true
}

# Что происходит:
# 1. Проверка доступности Telegram
# 2. Если доступен - отправка через Telegram
# 3. Если недоступен - автоматический fallback на SMS
# 4. Возврат информации о методе отправки
```

### **2. Проверка доступности:**

```python
# Проверка Telegram для номера
GET /api/auth/check-telegram/?phone=+1234567890

# Ответ:
{
    "telegram_available": true,
    "phone": "+1234567890"
}
```

### **3. SMS Fallback:**

```python
# Принудительная отправка SMS
POST /api/auth/send-sms-fallback/
{
    "phone": "+1234567890"
}

# Ответ:
{
    "message": "Код отправлен по SMS",
    "phone": "+1234567890"
}
```

## 🛠️ **API Endpoints**

### **Основные endpoints:**

```
📱 OTP ENDPOINTS
├── POST /api/auth/send-code/           # Отправка кода (Telegram/SMS)
├── POST /api/auth/verify-code/         # Проверка кода
├── POST /api/auth/send-sms-fallback/   # SMS как резервный вариант
├── GET  /api/auth/check-telegram/      # Проверка доступности Telegram
└── GET  /api/auth/balance-info/        # Информация о балансах
```

### **Детальное описание:**

#### **1. Отправка кода:**

```http
POST /api/auth/send-code/
Content-Type: application/json

{
    "phone": "+1234567890",
    "prefer_telegram": true
}

# Ответ при успехе:
{
    "message": "Код отправлен в Telegram",
    "phone": "+1234567890",
    "method": "telegram",
    "telegram_available": true,
    "fallback_required": false
}

# Ответ при fallback на SMS:
{
    "message": "Telegram недоступен. Код отправлен по SMS",
    "phone": "+1234567890",
    "method": "sms",
    "telegram_available": false,
    "fallback_required": false
}
```

#### **2. Проверка кода:**

```http
POST /api/auth/verify-code/
Content-Type: application/json

{
    "phone": "+1234567890",
    "code": "123456"
}

# Ответ:
{
    "message": "Код подтвержден успешно",
    "phone": "+1234567890",
    "verified": true
}
```

#### **3. Проверка доступности Telegram:**

```http
GET /api/auth/check-telegram/?phone=+1234567890

# Ответ:
{
    "telegram_available": true,
    "phone": "+1234567890"
}
```

#### **4. SMS Fallback:**

```http
POST /api/auth/send-sms-fallback/
Content-Type: application/json

{
    "phone": "+1234567890"
}

# Ответ:
{
    "message": "Код отправлен по SMS",
    "phone": "+1234567890"
}
```

#### **5. Информация о балансах:**

```http
GET /api/auth/balance-info/

# Ответ:
{
    "telegram_available": true,
    "sms_balance": 100.0
}
```

## 🔄 **Процесс работы**

### **Сценарий 1: Telegram доступен**

```
1. Пользователь → POST /send-code/ (prefer_telegram: true)
2. Система → Проверка доступности Telegram
3. Telegram → Отправка OTP кода
4. Пользователь → Получает код в Telegram
5. Пользователь → POST /verify-code/ с кодом
6. Система → Проверка через Telegram API
7. Успех → Пользователь аутентифицирован
```

### **Сценарий 2: Telegram недоступен**

```
1. Пользователь → POST /send-code/ (prefer_telegram: true)
2. Система → Проверка доступности Telegram
3. Telegram → Недоступен (пользователь не зарегистрирован)
4. Система → Автоматический fallback на SMS
5. Green SMS → Отправка SMS кода
6. Пользователь → Получает SMS
7. Пользователь → POST /verify-code/ с кодом
8. Система → Проверка через SMS сервис
9. Успех → Пользователь аутентифицирован
```

### **Сценарий 3: Принудительная отправка SMS**

```
1. Пользователь → POST /send-sms-fallback/
2. Система → Прямая отправка через SMS
3. Green SMS → Отправка SMS кода
4. Пользователь → Получает SMS
5. Пользователь → POST /verify-code/ с кодом
6. Система → Проверка через SMS сервис
7. Успех → Пользователь аутентифицирован
```

## 🎭 **Пользовательский интерфейс**

### **Рекомендуемый UX:**

```javascript
// 1. Проверка доступности Telegram
const checkTelegram = async (phone) => {
    const response = await fetch(`/api/auth/check-telegram/?phone=${phone}`);
    const data = await response.json();
    return data.telegram_available;
};

// 2. Отправка кода с предпочтением Telegram
const sendCode = async (phone) => {
    const response = await fetch('/api/auth/send-code/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            phone: phone,
            prefer_telegram: true
        })
    });
    const data = await response.json();
    
    if (data.method === 'telegram') {
        showMessage('Код отправлен в Telegram');
    } else if (data.method === 'sms') {
        showMessage('Код отправлен по SMS');
        showSMSFallbackButton(); // Показать кнопку "Отправить SMS"
    }
};

// 3. Fallback на SMS
const sendSMSFallback = async (phone) => {
    const response = await fetch('/api/auth/send-sms-fallback/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone: phone })
    });
    const data = await response.json();
    showMessage(data.message);
};
```

## 🔐 **Безопасность**

### **Rate Limiting:**

```python
# Ограничения применяются ко всем методам:
# - 5 запросов в час на номер
# - 5 попыток ввода кода в час
# - Автоматическая блокировка при превышении
```

### **Валидация:**

```python
# Проверки для всех кодов:
# 1. Код существует в БД
# 2. Код не использован
# 3. Код не истек (5 минут)
# 4. Номер телефона совпадает
# 5. Проверка через соответствующий API
```

## 📊 **Мониторинг и аналитика**

### **Отслеживание методов:**

```python
# В базе данных сохраняется:
# - request_id (для Telegram)
# - method (telegram/sms)
# - delivery_status
# - verification_status
```

### **Статистика:**

```python
# Метрики для анализа:
# - Количество Telegram отправок
# - Количество SMS отправок
# - Процент успешных доставок
# - Время отклика API
# - Стоимость отправок
```

## 🚨 **Обработка ошибок**

### **Типы ошибок:**

```python
# Telegram недоступен
{
    "error": "Telegram недоступен для данного номера"
}

# SMS недоступен
{
    "error": "Ошибка отправки SMS"
}

# Rate limiting
{
    "error": "Превышен лимит запросов"
}

# Неверный код
{
    "error": "Неверный или истекший код"
}
```

### **Логирование:**

```python
# Логи для отладки:
# - Попытки отправки через Telegram
# - Fallback на SMS
# - Статусы доставки
# - Ошибки API
```

## 🔧 **Конфигурация Ansible**

### **Переменные для деплоя:**

```yaml
# group_vars/production.yml
telegram_gateway_enabled: true
telegram_gateway_token: "{{ vault_telegram_gateway_token }}"
telegram_gateway_debug: false
```

### **Шаблон .env:**

```jinja2
# roles/django_app/templates/env.j2
TELEGRAM_GATEWAY_ENABLED={{ telegram_gateway_enabled | lower }}
TELEGRAM_GATEWAY_TOKEN={{ telegram_gateway_token }}
TELEGRAM_GATEWAY_DEBUG={{ telegram_gateway_debug | lower }}
```

## 📈 **Производительность**

### **Оптимизация:**

- **Кэширование** - результаты проверки доступности
- **Connection pooling** - переиспользование соединений
- **Batch операции** - группировка запросов
- **Async обработка** - неблокирующие операции

### **Метрики:**

```python
# Ключевые показатели:
# - Время отклика Telegram API
# - Время отклика SMS API
# - Процент успешных доставок
# - Стоимость отправок
```

## 🆘 **Устранение проблем**

### **Проблема: Telegram не работает**

```python
# Проверка настроек
print(f"Enabled: {settings.TELEGRAM_GATEWAY_ENABLED}")
print(f"Token: {settings.TELEGRAM_GATEWAY_TOKEN[:10]}...")
print(f"Debug: {settings.TELEGRAM_GATEWAY_DEBUG}")

# Проверка доступности
telegram_service = TelegramGatewayService()
available = telegram_service.is_telegram_available("+1234567890")
print(f"Available: {available}")
```

### **Проблема: SMS fallback не работает**

```python
# Проверка SMS сервиса
sms_service = GreenSMSService()
balance = sms_service.get_balance()
print(f"SMS Balance: {balance}")

# Проверка отправки
result = sms_service.send_verification_code("+1234567890")
print(f"SMS Result: {result}")
```

## 📚 **Дополнительные ресурсы**

- [Telegram Gateway API](https://gatewayapi.telegram.org/)
- [Telegram Gateway Tutorial](https://core.telegram.org/bots/api)
- [Green SMS API](https://docs.green-api.com/)
- [Django Redis](https://github.com/jazzband/django-redis)

---

**Теперь ваш проект поддерживает как Telegram OTP, так и SMS коды с автоматическим fallback! 🚀📱**
