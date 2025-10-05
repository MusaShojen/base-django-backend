# 🔴 Redis Guide - Полное руководство

Руководство по использованию Redis в Django проекте.

## 🎯 **Что такое Redis?**

**Redis** (Remote Dictionary Server) - это **in-memory база данных**, которая хранит данные в оперативной памяти. Это делает её **очень быстрой** для чтения и записи.

## 🚀 **Зачем нужен Redis в Django?**

### **1. Кэширование** ⚡
```python
# Без Redis - медленно
def get_user_profile(user_id):
    # Каждый раз идет запрос в PostgreSQL
    return User.objects.get(id=user_id)

# С Redis - быстро
def get_user_profile(user_id):
    # Сначала проверяем кэш
    cached = cache.get(f'user_{user_id}')
    if cached:
        return cached
    
    # Если нет в кэше - идем в БД
    user = User.objects.get(id=user_id)
    cache.set(f'user_{user_id}', user, 300)  # 5 минут
    return user
```

### **2. Сессии пользователей** 👤
```python
# Django настройки
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Теперь сессии хранятся в Redis, а не в БД
```

### **3. Rate Limiting** 🚦
```python
# Ограничение запросов
def rate_limit(request):
    key = f"rate_limit_{request.META['REMOTE_ADDR']}"
    current = cache.get(key, 0)
    
    if current >= 100:  # 100 запросов в час
        return HttpResponse("Too Many Requests", status=429)
    
    cache.set(key, current + 1, 3600)  # 1 час
    return None
```

### **4. Очереди задач** 📋
```python
# Celery + Redis для фоновых задач
from celery import Celery

app = Celery('myapp')
app.config_from_object('django.conf:settings', namespace='CELERY')

@app.task
def send_email_task(user_email, message):
    # Отправка email в фоне
    send_mail('Subject', message, 'from@example.com', [user_email])
```

## 🏗️ **Архитектура Redis в проекте**

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Django    │───▶│    Redis    │───▶│ PostgreSQL  │
│   App       │    │   (Cache)   │    │   (Data)    │
└─────────────┘    └─────────────┘    └─────────────┘
```

### **Что хранится в Redis:**

1. **Кэш данных** - часто используемые данные
2. **Сессии** - информация о пользователях
3. **Очереди** - фоновые задачи
4. **Rate limiting** - ограничения запросов
5. **Временные данные** - токены, коды подтверждения

## ⚙️ **Настройка Redis**

### **Django настройки:**

```python
# settings.py
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/0')

# Кэширование
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Сессии в Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24 часа
```

### **Переменные окружения:**

```bash
# .env
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=your-redis-password
```

## 🛠️ **Использование Redis в коде**

### **Базовые операции:**

```python
from django.core.cache import cache

# Сохранение данных
cache.set('key', 'value', 300)  # 5 минут

# Получение данных
value = cache.get('key')

# Удаление данных
cache.delete('key')

# Проверка существования
if cache.has_key('key'):
    value = cache.get('key')
```

### **Кэширование моделей:**

```python
def get_user_profile(user_id):
    # Проверяем кэш
    cached = cache.get(f'user_{user_id}')
    if cached:
        return cached
    
    # Получаем из БД
    user = User.objects.get(id=user_id)
    
    # Сохраняем в кэш на 5 минут
    cache.set(f'user_{user_id}', user, 300)
    
    return user
```

### **Rate Limiting:**

```python
def check_rate_limit(identifier, limit=100, window=3600):
    key = f"rate_limit_{identifier}"
    current = cache.get(key, 0)
    
    if current >= limit:
        return False
    
    cache.set(key, current + 1, window)
    return True
```

## 📊 **Мониторинг Redis**

### **Проверка статуса:**

```bash
# Подключение к Redis
redis-cli

# Проверка статуса
redis-cli ping

# Информация о сервере
redis-cli info

# Количество ключей
redis-cli dbsize

# Память
redis-cli info memory
```

### **Полезные команды:**

```bash
# Список всех ключей
redis-cli keys "*"

# Получить значение ключа
redis-cli get "key"

# Установить TTL
redis-cli expire "key" 300

# Удалить ключ
redis-cli del "key"
```

## 🔧 **Оптимизация Redis**

### **Настройки производительности:**

```bash
# redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### **Мониторинг производительности:**

```bash
# Статистика команд
redis-cli info commandstats

# Статистика памяти
redis-cli info memory

# Статистика клиентов
redis-cli info clients
```

## 🚨 **Устранение проблем**

### **Проблема: Redis не запускается**

```bash
# Проверить статус
systemctl status redis

# Перезапустить
systemctl restart redis

# Проверить логи
journalctl -u redis -f
```

### **Проблема: Высокое использование памяти**

```bash
# Проверить память
redis-cli info memory

# Очистить кэш
redis-cli flushdb

# Настроить политику удаления
redis-cli config set maxmemory-policy allkeys-lru
```

### **Проблема: Медленные запросы**

```bash
# Мониторинг медленных команд
redis-cli slowlog get 10

# Настройка лимита медленных команд
redis-cli config set slowlog-log-slower-than 10000
```

## 📈 **Метрики и мониторинг**

### **Ключевые метрики:**

1. **Использование памяти** - не должно превышать 80%
2. **Количество подключений** - мониторить активные соединения
3. **Команды в секунду** - производительность
4. **Hit ratio** - эффективность кэша

### **Настройка мониторинга:**

```bash
# Установка Redis Exporter для Prometheus
docker run -d --name redis-exporter \
  -p 9121:9121 \
  oliver006/redis_exporter
```

## 🔐 **Безопасность Redis**

### **Настройки безопасности:**

```bash
# redis.conf
requirepass your-strong-password
bind 127.0.0.1
protected-mode yes
```

### **Firewall:**

```bash
# Разрешить только локальные подключения
ufw allow from 127.0.0.1 to any port 6379
ufw deny 6379
```

## 📚 **Полезные команды**

### **Управление Redis:**

```bash
# Статус сервиса
systemctl status redis

# Перезапуск
systemctl restart redis

# Логи
journalctl -u redis -f

# Конфигурация
redis-cli config get "*"
```

### **Отладка:**

```bash
# Подключение
redis-cli -a your-password

# Мониторинг команд
redis-cli monitor

# Информация о сервере
redis-cli info server
```

## 🎯 **Лучшие практики**

### **1. Ключи:**
- Используйте префиксы: `user:123`, `session:abc`
- Устанавливайте TTL для временных данных
- Избегайте слишком длинных ключей

### **2. Память:**
- Настройте политику удаления: `allkeys-lru`
- Мониторьте использование памяти
- Используйте сжатие для больших данных

### **3. Производительность:**
- Используйте pipeline для множественных операций
- Кэшируйте часто используемые данные
- Настройте персистентность правильно

## 📖 **Дополнительные ресурсы**

- [Redis документация](https://redis.io/documentation)
- [Django Redis](https://github.com/jazzband/django-redis)
- [Redis команды](https://redis.io/commands)
- [Redis конфигурация](https://redis.io/topics/config)

---

**Redis - это мощный инструмент для ускорения вашего Django приложения! 🚀**
