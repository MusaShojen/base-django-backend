from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


def require_roles(*allowed_roles):
    """
    Декоратор для проверки ролей пользователя
    
    Args:
        *allowed_roles: Список разрешенных ролей ('user', 'admin', 'superadmin')
    
    Usage:
        @require_roles('admin', 'superadmin')
        def admin_view(request):
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Проверяем, аутентифицирован ли пользователь
            if not request.user.is_authenticated:
                return Response(
                    {'error': 'Требуется аутентификация'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Проверяем, есть ли у пользователя нужная роль
            if not request.user.has_any_role(allowed_roles):
                return Response(
                    {'error': 'Недостаточно прав доступа'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_admin(view_func):
    """
    Декоратор для проверки прав администратора
    """
    return require_roles('admin', 'superadmin')(view_func)


def require_superadmin(view_func):
    """
    Декоратор для проверки прав супер администратора
    """
    return require_roles('superadmin')(view_func)


def require_phone_verified(view_func):
    """
    Декоратор для проверки подтверждения телефона
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Требуется аутентификация'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not request.user.is_phone_verified:
            return Response(
                {'error': 'Требуется подтверждение номера телефона'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        return view_func(request, *args, **kwargs)
    return wrapper
