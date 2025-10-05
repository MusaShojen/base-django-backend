"""
Валидаторы для номеров телефонов
"""
import re
from django.core.exceptions import ValidationError


def validate_phone_number(phone):
    """
    Валидирует номер телефона в формате E.164
    
    Args:
        phone: Номер телефона для валидации
        
    Returns:
        bool: True если номер валиден
        
    Raises:
        ValidationError: Если номер невалиден
    """
    if not phone:
        raise ValidationError('Номер телефона обязателен')
    
    # Убираем все пробелы и дефисы
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Проверяем формат E.164: +[код страны][номер]
    # Длина: от 7 до 15 цифр после +
    e164_pattern = r'^\+[1-9]\d{6,14}$'
    
    if not re.match(e164_pattern, phone):
        raise ValidationError(
            'Номер телефона должен быть в международном формате E.164 '
            '(например: +1234567890, +79123456789)'
        )
    
    # Проверяем длину (7-15 цифр после +)
    digits_only = phone[1:]  # Убираем +
    if len(digits_only) < 7 or len(digits_only) > 15:
        raise ValidationError(
            'Номер телефона должен содержать от 7 до 15 цифр'
        )
    
    return True


def normalize_phone_number(phone):
    """
    Нормализует номер телефона к формату E.164
    
    Args:
        phone: Номер телефона для нормализации
        
    Returns:
        str: Нормализованный номер в формате E.164
        
    Raises:
        ValidationError: Если номер не может быть нормализован
    """
    if not phone:
        raise ValidationError('Номер телефона обязателен')
    
    # Убираем все пробелы, дефисы, скобки
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Если номер начинается с 8 (Россия), заменяем на +7
    if phone.startswith('8') and len(phone) == 11:
        phone = '+7' + phone[1:]
    
    # Если номер начинается с 7 (Россия), добавляем +
    elif phone.startswith('7') and len(phone) == 11:
        phone = '+' + phone
    
    # Если номер не начинается с +, добавляем его
    elif not phone.startswith('+'):
        phone = '+' + phone
    
    # Валидируем результат
    validate_phone_number(phone)
    
    return phone


def get_country_code(phone):
    """
    Извлекает код страны из номера телефона
    
    Args:
        phone: Номер телефона в формате E.164
        
    Returns:
        str: Код страны
    """
    if not phone.startswith('+'):
        return None
    
    # Известные коды стран (основные)
    country_codes = {
        '1': 'US/CA',      # США/Канада
        '7': 'RU/KZ',      # Россия/Казахстан
        '380': 'UA',       # Украина
        '375': 'BY',       # Беларусь
        '998': 'UZ',       # Узбекистан
        '996': 'KG',       # Кыргызстан
        '992': 'TJ',       # Таджикистан
        '993': 'TM',       # Туркменистан
        '374': 'AM',       # Армения
        '995': 'GE',       # Грузия
        '994': 'AZ',       # Азербайджан
        '90': 'TR',        # Турция
        '86': 'CN',        # Китай
        '81': 'JP',        # Япония
        '82': 'KR',        # Южная Корея
        '91': 'IN',        # Индия
        '44': 'GB',        # Великобритания
        '49': 'DE',        # Германия
        '33': 'FR',        # Франция
        '39': 'IT',        # Италия
        '34': 'ES',        # Испания
    }
    
    # Пробуем найти код страны
    for code_length in [3, 2, 1]:  # Проверяем от длинных к коротким
        if len(phone) > code_length:
            code = phone[1:1+code_length]  # Убираем + и берем код
            if code in country_codes:
                return code
    
    return None


def format_phone_display(phone):
    """
    Форматирует номер телефона для отображения
    
    Args:
        phone: Номер телефона в формате E.164
        
    Returns:
        str: Отформатированный номер
    """
    if not phone or not phone.startswith('+'):
        return phone
    
    # Убираем +
    digits = phone[1:]
    
    # Форматируем в зависимости от длины
    if len(digits) == 11 and digits.startswith('7'):  # Россия
        return f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:]}"
    elif len(digits) == 10 and digits.startswith('1'):  # США/Канада
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    else:
        # Общий формат
        return f"+{digits[:2]} {digits[2:5]} {digits[5:8]} {digits[8:]}"


def is_valid_phone_format(phone):
    """
    Проверяет, является ли номер валидным без выброса исключения
    
    Args:
        phone: Номер телефона для проверки
        
    Returns:
        bool: True если номер валиден
    """
    try:
        validate_phone_number(phone)
        return True
    except ValidationError:
        return False
