"""
Утилиты для работы с кэшем Redis
"""
from django.core.cache import cache
from django.conf import settings
import json
import hashlib
from typing import Any, Optional, Dict


class CacheManager:
    """Менеджер кэша для работы с Redis"""
    
    @staticmethod
    def get_user_cache_key(user_id: int, prefix: str = 'user') -> str:
        """Генерирует ключ кэша для пользователя"""
        return f"{prefix}_{user_id}"
    
    @staticmethod
    def get_api_cache_key(endpoint: str, params: Dict = None) -> str:
        """Генерирует ключ кэша для API запроса"""
        if params:
            params_str = json.dumps(params, sort_keys=True)
            params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
            return f"api_{endpoint}_{params_hash}"
        return f"api_{endpoint}"
    
    @staticmethod
    def cache_user_data(user_id: int, data: Dict, timeout: int = 300) -> None:
        """Кэширует данные пользователя"""
        key = CacheManager.get_user_cache_key(user_id)
        cache.set(key, data, timeout)
    
    @staticmethod
    def get_cached_user_data(user_id: int) -> Optional[Dict]:
        """Получает кэшированные данные пользователя"""
        key = CacheManager.get_user_cache_key(user_id)
        return cache.get(key)
    
    @staticmethod
    def invalidate_user_cache(user_id: int) -> None:
        """Удаляет кэш пользователя"""
        key = CacheManager.get_user_cache_key(user_id)
        cache.delete(key)
    
    @staticmethod
    def cache_api_response(endpoint: str, params: Dict, response: Any, timeout: int = 60) -> None:
        """Кэширует ответ API"""
        key = CacheManager.get_api_cache_key(endpoint, params)
        cache.set(key, response, timeout)
    
    @staticmethod
    def get_cached_api_response(endpoint: str, params: Dict) -> Optional[Any]:
        """Получает кэшированный ответ API"""
        key = CacheManager.get_api_cache_key(endpoint, params)
        return cache.get(key)


class RateLimiter:
    """Ограничитель скорости запросов"""
    
    @staticmethod
    def check_rate_limit(identifier: str, limit: int = 100, window: int = 3600) -> bool:
        """
        Проверяет лимит запросов
        
        Args:
            identifier: Идентификатор (IP, user_id, etc.)
            limit: Максимальное количество запросов
            window: Окно времени в секундах
        
        Returns:
            True если лимит не превышен, False если превышен
        """
        key = f"rate_limit_{identifier}"
        current = cache.get(key, 0)
        
        if current >= limit:
            return False
        
        # Увеличиваем счетчик
        cache.set(key, current + 1, window)
        return True
    
    @staticmethod
    def get_remaining_requests(identifier: str, limit: int = 100) -> int:
        """Получает количество оставшихся запросов"""
        key = f"rate_limit_{identifier}"
        current = cache.get(key, 0)
        return max(0, limit - current)


class SessionManager:
    """Менеджер сессий в Redis"""
    
    @staticmethod
    def create_user_session(user_id: int, session_data: Dict) -> str:
        """Создает сессию пользователя"""
        session_key = f"session_{user_id}_{hashlib.md5(str(session_data).encode()).hexdigest()[:8]}"
        cache.set(session_key, session_data, settings.SESSION_COOKIE_AGE)
        return session_key
    
    @staticmethod
    def get_user_session(session_key: str) -> Optional[Dict]:
        """Получает сессию пользователя"""
        return cache.get(session_key)
    
    @staticmethod
    def update_user_session(session_key: str, session_data: Dict) -> None:
        """Обновляет сессию пользователя"""
        cache.set(session_key, session_data, settings.SESSION_COOKIE_AGE)
    
    @staticmethod
    def delete_user_session(session_key: str) -> None:
        """Удаляет сессию пользователя"""
        cache.delete(session_key)


class SMSVerificationCache:
    """Кэш для SMS верификации"""
    
    @staticmethod
    def store_verification_code(phone: str, code: str, timeout: int = 300) -> None:
        """Сохраняет код верификации"""
        key = f"sms_verification_{phone}"
        cache.set(key, code, timeout)
    
    @staticmethod
    def get_verification_code(phone: str) -> Optional[str]:
        """Получает код верификации"""
        key = f"sms_verification_{phone}"
        return cache.get(key)
    
    @staticmethod
    def delete_verification_code(phone: str) -> None:
        """Удаляет код верификации"""
        key = f"sms_verification_{phone}"
        cache.delete(key)
    
    @staticmethod
    def store_attempts(phone: str, attempts: int, timeout: int = 3600) -> None:
        """Сохраняет количество попыток"""
        key = f"sms_attempts_{phone}"
        cache.set(key, attempts, timeout)
    
    @staticmethod
    def get_attempts(phone: str) -> int:
        """Получает количество попыток"""
        key = f"sms_attempts_{phone}"
        return cache.get(key, 0)
    
    @staticmethod
    def increment_attempts(phone: str, max_attempts: int = 5) -> bool:
        """Увеличивает количество попыток"""
        attempts = SMSVerificationCache.get_attempts(phone)
        if attempts >= max_attempts:
            return False
        
        SMSVerificationCache.store_attempts(phone, attempts + 1)
        return True
