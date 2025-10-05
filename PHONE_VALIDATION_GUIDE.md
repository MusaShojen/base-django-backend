# 📱 Phone Number Validation Guide

Руководство по валидации номеров телефонов в международном формате E.164.

## 🌍 **Международный формат E.164**

### **✅ Что такое E.164:**

**E.164** - это международный стандарт для номеров телефонов, который используется:
- **Telegram Gateway API** - требует формат E.164
- **Green SMS API** - поддерживает E.164
- **Международные сервисы** - стандарт для глобальных приложений

### **📋 Формат E.164:**

```
+[код страны][номер]
```

**Правила:**
- Начинается с `+`
- Код страны: 1-3 цифры
- Номер: 6-14 цифр
- Общая длина: 7-15 цифр после `+`

## 🔧 **Валидация в проекте**

### **Автоматическая нормализация:**

```python
# Входные данные → Нормализованный формат
"8 912 345 67 89" → "+79123456789"
"7 912 345 67 89" → "+79123456789"  
"79123456789" → "+79123456789"
"+79123456789" → "+79123456789"
"8-912-345-67-89" → "+79123456789"
```

### **Поддерживаемые форматы ввода:**

```python
# Россия
"+79123456789"     # ✅ Правильно
"79123456789"      # ✅ Автоматически станет +79123456789
"8 912 345 67 89"  # ✅ Автоматически станет +79123456789
"8-912-345-67-89"  # ✅ Автоматически станет +79123456789

# США/Канада
"+1234567890"      # ✅ Правильно
"1234567890"       # ✅ Автоматически станет +1234567890

# Украина
"+380123456789"    # ✅ Правильно
"380123456789"     # ✅ Автоматически станет +380123456789
```

## 🛠️ **Использование валидаторов**

### **Базовое использование:**

```python
from authentication.validators import validate_phone_number, normalize_phone_number

# Валидация
try:
    validate_phone_number("+79123456789")
    print("Номер валиден")
except ValidationError as e:
    print(f"Ошибка: {e}")

# Нормализация
normalized = normalize_phone_number("8 912 345 67 89")
print(normalized)  # "+79123456789"
```

### **В сериализаторах:**

```python
class PhoneVerificationSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    
    def validate_phone(self, value):
        try:
            return normalize_phone_number(value)
        except Exception as e:
            raise serializers.ValidationError(f"Ошибка: {e}")
```

## 📊 **Примеры валидации**

### **✅ Валидные номера:**

```python
# Россия
"+79123456789"     # 11 цифр
"+7912345678"       # 10 цифр
"+791234567890"     # 12 цифр

# США/Канада
"+1234567890"       # 10 цифр
"+12345678901"      # 11 цифр

# Украина
"+380123456789"     # 12 цифр

# Другие страны
"+8612345678901"    # Китай
"+81123456789"      # Япония
```

### **❌ Невалидные номера:**

```python
# Неправильные форматы
"79123456789"       # Нет +
"+791234567"        # Слишком короткий
"+791234567890123"  # Слишком длинный
"+079123456789"     # Начинается с 0
"+79123456789a"     # Содержит буквы
"79123456789+"      # + не в начале
```

## 🎯 **API Endpoints**

### **Отправка кода:**

```http
POST /api/auth/send-code/
Content-Type: application/json

{
    "phone": "+79123456789"  # E.164 формат
}

# Или с автоматической нормализацией:
{
    "phone": "8 912 345 67 89"  # Будет нормализован до +79123456789
}
```

### **Проверка кода:**

```http
POST /api/auth/verify-code/
Content-Type: application/json

{
    "phone": "+79123456789",
    "code": "123456"
}
```

### **Проверка доступности Telegram:**

```http
GET /api/auth/check-telegram/?phone=+79123456789

# Ответ:
{
    "telegram_available": true,
    "phone": "+79123456789"
}
```

## 🔍 **Детальная валидация**

### **Проверка кода страны:**

```python
from authentication.validators import get_country_code

# Получение кода страны
country_code = get_country_code("+79123456789")
print(country_code)  # "7" (Россия)

country_code = get_country_code("+1234567890")
print(country_code)  # "1" (США/Канада)
```

### **Форматирование для отображения:**

```python
from authentication.validators import format_phone_display

# Форматирование для UI
formatted = format_phone_display("+79123456789")
print(formatted)  # "+7 (912) 345-67-89"

formatted = format_phone_display("+1234567890")
print(formatted)  # "+1 (234) 567-890"
```

## 🚨 **Обработка ошибок**

### **Типы ошибок валидации:**

```python
# 1. Пустой номер
{
    "phone": ["Номер телефона обязателен"]
}

# 2. Неправильный формат
{
    "phone": ["Номер телефона должен быть в международном формате E.164 (например: +1234567890, +79123456789)"]
}

# 3. Слишком короткий
{
    "phone": ["Номер телефона должен содержать от 7 до 15 цифр"]
}

# 4. Слишком длинный
{
    "phone": ["Номер телефона должен содержать от 7 до 15 цифр"]
}

# 5. Начинается с 0
{
    "phone": ["Номер телефона должен быть в международном формате E.164"]
}
```

### **Логирование ошибок:**

```python
# В views.py
try:
    serializer = PhoneVerificationSerializer(data=request.data)
    if serializer.is_valid():
        phone = serializer.validated_data['phone']  # Уже нормализован
        # ... обработка
    else:
        return Response(serializer.errors, status=400)
except Exception as e:
    logger.error(f"Ошибка валидации телефона: {e}")
    return Response({'error': 'Ошибка валидации'}, status=500)
```

## 🌐 **Поддержка стран**

### **Основные коды стран:**

```python
# СНГ и Восточная Европа
"+7"    # Россия, Казахстан
"+380"  # Украина
"+375"  # Беларусь
"+998"  # Узбекистан
"+996"  # Кыргызстан
"+992"  # Таджикистан
"+993"  # Туркменистан
"+374"  # Армения
"+995"  # Грузия
"+994"  # Азербайджан

# Западная Европа
"+44"   # Великобритания
"+49"   # Германия
"+33"   # Франция
"+39"   # Италия
"+34"   # Испания

# Северная Америка
"+1"    # США, Канада

# Азия
"+86"   # Китай
"+81"   # Япония
"+82"   # Южная Корея
"+91"   # Индия
"+90"   # Турция
```

## 🔧 **Настройка для разных регионов**

### **Российские номера:**

```python
# Поддерживаемые форматы:
"8 912 345 67 89"    # → +79123456789
"7 912 345 67 89"    # → +79123456789
"+7 912 345 67 89"   # → +79123456789
"8-912-345-67-89"    # → +79123456789
"8(912)345-67-89"    # → +79123456789
```

### **Американские номера:**

```python
# Поддерживаемые форматы:
"1234567890"         # → +1234567890
"+1 234 567 890"     # → +1234567890
"1-234-567-890"      # → +1234567890
```

## 📈 **Производительность**

### **Оптимизация валидации:**

```python
# Кэширование результатов валидации
from django.core.cache import cache

def validate_phone_cached(phone):
    cache_key = f"phone_validation_{phone}"
    result = cache.get(cache_key)
    
    if result is None:
        result = validate_phone_number(phone)
        cache.set(cache_key, result, 3600)  # 1 час
    
    return result
```

### **Batch валидация:**

```python
# Валидация множества номеров
def validate_phones_batch(phones):
    results = []
    for phone in phones:
        try:
            normalized = normalize_phone_number(phone)
            results.append({'phone': phone, 'normalized': normalized, 'valid': True})
        except Exception as e:
            results.append({'phone': phone, 'error': str(e), 'valid': False})
    return results
```

## 🆘 **Устранение проблем**

### **Проблема: Номер не валидируется**

```python
# Проверка пошагово
phone = "8 912 345 67 89"

# 1. Очистка
cleaned = re.sub(r'[\s\-\(\)]', '', phone)
print(f"Очищенный: {cleaned}")  # "89123456789"

# 2. Нормализация
if cleaned.startswith('8') and len(cleaned) == 11:
    normalized = '+7' + cleaned[1:]
    print(f"Нормализованный: {normalized}")  # "+79123456789"

# 3. Валидация
validate_phone_number(normalized)
```

### **Проблема: API не принимает номер**

```python
# Проверка формата для API
def check_api_format(phone):
    # Telegram Gateway требует E.164
    if not phone.startswith('+'):
        return False
    
    # Проверка длины
    digits = phone[1:]
    if len(digits) < 7 or len(digits) > 15:
        return False
    
    return True
```

## 📚 **Дополнительные ресурсы**

- [E.164 стандарт](https://en.wikipedia.org/wiki/E.164)
- [Telegram Gateway API](https://gatewayapi.telegram.org/)
- [Django валидация](https://docs.djangoproject.com/en/stable/ref/validators/)
- [Python regex](https://docs.python.org/3/library/re.html)

---

**Теперь ваши номера телефонов валидируются по международному стандарту E.164! 🌍📱**
