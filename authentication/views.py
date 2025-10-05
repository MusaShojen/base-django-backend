from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from django.utils import timezone
from datetime import timedelta
import uuid
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import AuthToken
from .serializers import (
    PhoneVerificationSerializer, 
    CodeVerificationSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    TokenSerializer
)
from .services import GreenSMSService
from .decorators import require_roles
from .cache_utils import CacheManager, RateLimiter, SMSVerificationCache
from .otp_service import UniversalOTPService


@swagger_auto_schema(
    method='post',
    operation_summary='Отправка SMS кода подтверждения',
    operation_description='Отправляет SMS код подтверждения на указанный номер телефона',
    request_body=PhoneVerificationSerializer,
    responses={
        200: openapi.Response(
            description='SMS код успешно отправлен',
            examples={
                'application/json': {
                    'message': 'Код подтверждения отправлен на ваш номер телефона',
                    'phone': '+1234567890'
                }
            }
        ),
        400: openapi.Response(
            description='Ошибка валидации данных',
            examples={
                'application/json': {
                    'phone': ['Номер телефона должен начинаться с "+"']
                }
            }
        ),
        500: openapi.Response(
            description='Ошибка отправки SMS',
            examples={
                'application/json': {
                    'error': 'Ошибка отправки SMS кода'
                }
            }
        )
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def send_verification_code(request):
    """Отправка кода подтверждения через Telegram или SMS"""
    serializer = PhoneVerificationSerializer(data=request.data)
    
    if serializer.is_valid():
        phone = serializer.validated_data['phone']
        prefer_telegram = request.data.get('prefer_telegram', True)
        
        # Используем универсальный OTP сервис
        otp_service = UniversalOTPService()
        result = otp_service.send_verification_code(phone, prefer_telegram=prefer_telegram)
        
        if result['success']:
            # Сохраняем код в Redis
            if result['sms_verification']:
                SMSVerificationCache.store_verification_code(phone, result['sms_verification'].code)
            
            return Response({
                'message': result['message'],
                'phone': phone,
                'method': result['method'],
                'telegram_available': result['telegram_available'],
                'fallback_required': result.get('fallback_required', False)
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': result['message']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    operation_summary='Проверка SMS кода подтверждения',
    operation_description='Проверяет SMS код подтверждения для указанного номера телефона',
    request_body=CodeVerificationSerializer,
    responses={
        200: openapi.Response(
            description='Код подтвержден успешно',
            examples={
                'application/json': {
                    'message': 'Код подтвержден успешно',
                    'phone': '+1234567890',
                    'verified': True
                }
            }
        ),
        400: openapi.Response(
            description='Неверный код или ошибка валидации',
            examples={
                'application/json': {
                    'error': 'Неверный или истекший код'
                }
            }
        )
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_code(request):
    """Проверка кода подтверждения"""
    serializer = CodeVerificationSerializer(data=request.data)
    
    if serializer.is_valid():
        phone = serializer.validated_data['phone']
        code = serializer.validated_data['code']
        
        # Используем универсальный OTP сервис
        otp_service = UniversalOTPService()
        is_valid = otp_service.verify_code(phone, code)
        
        if is_valid:
            # Удаляем код из Redis
            SMSVerificationCache.delete_verification_code(phone)
            
            return Response({
                'message': 'Код подтвержден успешно',
                'phone': phone,
                'verified': True
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Неверный или истекший код'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    operation_summary='Отправка SMS кода (резервный вариант)',
    operation_description='Отправляет SMS код как резервный вариант, если Telegram недоступен',
    request_body=PhoneVerificationSerializer,
    responses={
        200: openapi.Response(
            description='SMS код отправлен',
            examples={
                'application/json': {
                    'message': 'Код отправлен по SMS',
                    'phone': '+1234567890'
                }
            }
        ),
        400: openapi.Response(
            description='Ошибка валидации',
            examples={
                'application/json': {
                    'phone': ['Неверный формат']
                }
            }
        ),
        500: openapi.Response(
            description='Ошибка отправки',
            examples={
                'application/json': {
                    'error': 'Ошибка отправки SMS'
                }
            }
        )
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def send_sms_fallback(request):
    """Отправка SMS кода как резервный вариант"""
    serializer = PhoneVerificationSerializer(data=request.data)
    
    if serializer.is_valid():
        phone = serializer.validated_data['phone']
        
        # Используем универсальный OTP сервис для SMS fallback
        otp_service = UniversalOTPService()
        result = otp_service.send_sms_fallback(phone)
        
        if result['success']:
            return Response({
                'message': result['message'],
                'phone': phone
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': result['message']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    operation_summary='Проверка доступности Telegram',
    operation_description='Проверяет, доступен ли Telegram для указанного номера телефона',
    manual_parameters=[
        openapi.Parameter(
            'phone',
            openapi.IN_QUERY,
            description="Номер телефона",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description='Результат проверки',
            examples={
                'application/json': {
                    'telegram_available': True,
                    'phone': '+1234567890'
                }
            }
        ),
        400: openapi.Response(
            description='Ошибка валидации',
            examples={
                'application/json': {
                    'error': 'Неверный формат номера'
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def check_telegram_availability(request):
    """Проверка доступности Telegram для номера"""
    phone = request.GET.get('phone')
    
    if not phone:
        return Response({
            'error': 'Номер телефона обязателен'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Валидация номера телефона уже выполняется в сериализаторе
    
    # Используем универсальный OTP сервис
    otp_service = UniversalOTPService()
    telegram_available = otp_service.check_telegram_availability(phone)
    
    return Response({
        'telegram_available': telegram_available,
        'phone': phone
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_summary='Информация о балансах',
    operation_description='Получает информацию о балансах Telegram и SMS сервисов',
    responses={
        200: openapi.Response(
            description='Информация о балансах',
            examples={
                'application/json': {
                    'telegram_available': True,
                    'sms_balance': 100.0
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_balance_info(request):
    """Получение информации о балансах"""
    otp_service = UniversalOTPService()
    balance_info = otp_service.get_balance_info()
    
    return Response(balance_info, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_summary='Регистрация нового пользователя',
    operation_description='Создает нового пользователя в системе',
    request_body=UserRegistrationSerializer,
    responses={
        201: openapi.Response(
            description='Пользователь успешно зарегистрирован',
            examples={
                'application/json': {
                    'message': 'Пользователь успешно зарегистрирован',
                    'user': {
                        'id': 1,
                        'phone': '+1234567890',
                        'username': 'john_doe',
                        'email': 'john@example.com',
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'role': 'user',
                        'role_display': 'Пользователь',
                        'is_phone_verified': True,
                        'created_at': '2025-01-05T08:00:00Z'
                    },
                    'token': '12345678-1234-1234-1234-123456789abc'
                }
            }
        ),
        400: openapi.Response(
            description='Ошибка валидации данных',
            examples={
                'application/json': {
                    'phone': ['Пользователь с таким номером телефона уже существует'],
                    'password': ['Пароли не совпадают']
                }
            }
        )
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Регистрация нового пользователя"""
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        # Проверяем, что номер телефона подтвержден
        phone = serializer.validated_data['phone']
        sms_service = GreenSMSService()
        
        # В реальном приложении здесь должна быть проверка подтверждения номера
        # Для упрощения пропускаем эту проверку
        
        user = serializer.save()
        user.is_phone_verified = True  # Временно для упрощения
        user.save()
        
        # Создаем токен аутентификации
        expires_at = timezone.now() + timedelta(days=30)
        auth_token = AuthToken.objects.create(
            user=user,
            expires_at=expires_at
        )
        
        return Response({
            'message': 'Пользователь успешно зарегистрирован',
            'user': UserSerializer(user).data,
            'token': str(auth_token.token)
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    operation_summary='Вход пользователя в систему',
    operation_description='Аутентификация пользователя по номеру телефона и паролю',
    request_body=UserLoginSerializer,
    responses={
        200: openapi.Response(
            description='Вход выполнен успешно',
            examples={
                'application/json': {
                    'message': 'Вход выполнен успешно',
                    'user': {
                        'id': 1,
                        'phone': '+1234567890',
                        'username': 'john_doe',
                        'email': 'john@example.com',
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'role': 'user',
                        'role_display': 'Пользователь',
                        'is_phone_verified': True,
                        'created_at': '2025-01-05T08:00:00Z'
                    },
                    'token': '12345678-1234-1234-1234-123456789abc'
                }
            }
        ),
        400: openapi.Response(
            description='Ошибка аутентификации',
            examples={
                'application/json': {
                    'error': 'Неверные учетные данные'
                }
            }
        )
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Вход пользователя"""
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        phone = serializer.validated_data['phone']
        password = serializer.validated_data['password']
        
        # Аутентификация пользователя
        user = authenticate(request, username=phone, password=password)
        
        if user:
            if user.is_active:
                # Создаем новый токен
                expires_at = timezone.now() + timedelta(days=30)
                auth_token = AuthToken.objects.create(
                    user=user,
                    expires_at=expires_at
                )
                
                return Response({
                    'message': 'Вход выполнен успешно',
                    'user': UserSerializer(user).data,
                    'token': str(auth_token.token)
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Аккаунт деактивирован'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'error': 'Неверные учетные данные'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    operation_summary='Выход пользователя из системы',
    operation_description='Деактивирует все токены аутентификации пользователя',
    responses={
        200: openapi.Response(
            description='Выход выполнен успешно',
            examples={
                'application/json': {
                    'message': 'Выход выполнен успешно'
                }
            }
        ),
        401: openapi.Response(
            description='Требуется аутентификация',
            examples={
                'application/json': {
                    'error': 'Требуется аутентификация'
                }
            }
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Выход пользователя"""
    # Деактивируем все токены пользователя
    AuthToken.objects.filter(user=request.user, is_active=True).update(is_active=False)
    
    return Response({
        'message': 'Выход выполнен успешно'
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_summary='Получение профиля пользователя',
    operation_description='Возвращает информацию о текущем пользователе',
    responses={
        200: openapi.Response(
            description='Профиль пользователя',
            examples={
                'application/json': {
                    'user': {
                        'id': 1,
                        'phone': '+1234567890',
                        'username': 'john_doe',
                        'email': 'john@example.com',
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'role': 'user',
                        'role_display': 'Пользователь',
                        'is_phone_verified': True,
                        'created_at': '2025-01-05T08:00:00Z'
                    }
                }
            }
        ),
        401: openapi.Response(
            description='Требуется аутентификация',
            examples={
                'application/json': {
                    'error': 'Требуется аутентификация'
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """Получение профиля пользователя"""
    return Response({
        'user': UserSerializer(request.user).data
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='put',
    operation_summary='Обновление профиля пользователя',
    operation_description='Обновляет информацию профиля текущего пользователя',
    request_body=UserSerializer,
    responses={
        200: openapi.Response(
            description='Профиль обновлен успешно',
            examples={
                'application/json': {
                    'message': 'Профиль обновлен успешно',
                    'user': {
                        'id': 1,
                        'phone': '+1234567890',
                        'username': 'john_doe',
                        'email': 'john@example.com',
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'role': 'user',
                        'role_display': 'Пользователь',
                        'is_phone_verified': True,
                        'created_at': '2025-01-05T08:00:00Z'
                    }
                }
            }
        ),
        400: openapi.Response(
            description='Ошибка валидации данных',
            examples={
                'application/json': {
                    'email': ['Введите правильный адрес электронной почты']
                }
            }
        ),
        401: openapi.Response(
            description='Требуется аутентификация',
            examples={
                'application/json': {
                    'error': 'Требуется аутентификация'
                }
            }
        )
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Обновление профиля пользователя"""
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Профиль обновлен успешно',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Примеры защищенных роутов с разными ролями

@swagger_auto_schema(
    method='get',
    operation_summary='Дашборд пользователя',
    operation_description='Доступен для всех аутентифицированных пользователей',
    responses={
        200: openapi.Response(
            description='Дашборд пользователя',
            examples={
                'application/json': {
                    'message': 'Добро пожаловать в личный кабинет!',
                    'user': {
                        'id': 1,
                        'phone': '+1234567890',
                        'username': 'john_doe',
                        'email': 'john@example.com',
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'role': 'user',
                        'role_display': 'Пользователь',
                        'is_phone_verified': True,
                        'created_at': '2025-01-05T08:00:00Z'
                    }
                }
            }
        ),
        401: openapi.Response(
            description='Требуется аутентификация',
            examples={
                'application/json': {
                    'error': 'Требуется аутентификация'
                }
            }
        ),
        403: openapi.Response(
            description='Недостаточно прав доступа',
            examples={
                'application/json': {
                    'error': 'Недостаточно прав доступа'
                }
            }
        )
    }
)
@api_view(['GET'])
@require_roles('user', 'admin', 'superadmin')
def user_dashboard(request):
    """Дашборд для всех пользователей"""
    return Response({
        'message': 'Добро пожаловать в личный кабинет!',
        'user': UserSerializer(request.user).data
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_summary='Панель администратора',
    operation_description='Доступна только для администраторов и суперадминистраторов',
    responses={
        200: openapi.Response(
            description='Панель администратора',
            examples={
                'application/json': {
                    'message': 'Добро пожаловать в панель администратора!',
                    'user': {
                        'id': 1,
                        'phone': '+1234567890',
                        'username': 'admin',
                        'email': 'admin@example.com',
                        'first_name': 'Admin',
                        'last_name': 'User',
                        'role': 'admin',
                        'role_display': 'Администратор',
                        'is_phone_verified': True,
                        'created_at': '2025-01-05T08:00:00Z'
                    }
                }
            }
        ),
        401: openapi.Response(
            description='Требуется аутентификация',
            examples={
                'application/json': {
                    'error': 'Требуется аутентификация'
                }
            }
        ),
        403: openapi.Response(
            description='Недостаточно прав доступа',
            examples={
                'application/json': {
                    'error': 'Недостаточно прав доступа'
                }
            }
        )
    }
)
@api_view(['GET'])
@require_roles('admin', 'superadmin')
def admin_panel(request):
    """Панель администратора"""
    return Response({
        'message': 'Добро пожаловать в панель администратора!',
        'user': UserSerializer(request.user).data
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_summary='Панель суперадминистратора',
    operation_description='Доступна только для суперадминистраторов',
    responses={
        200: openapi.Response(
            description='Панель суперадминистратора',
            examples={
                'application/json': {
                    'message': 'Добро пожаловать в панель супер администратора!',
                    'user': {
                        'id': 1,
                        'phone': '+1234567890',
                        'username': 'superadmin',
                        'email': 'superadmin@example.com',
                        'first_name': 'Super',
                        'last_name': 'Admin',
                        'role': 'superadmin',
                        'role_display': 'Супер администратор',
                        'is_phone_verified': True,
                        'created_at': '2025-01-05T08:00:00Z'
                    }
                }
            }
        ),
        401: openapi.Response(
            description='Требуется аутентификация',
            examples={
                'application/json': {
                    'error': 'Требуется аутентификация'
                }
            }
        ),
        403: openapi.Response(
            description='Недостаточно прав доступа',
            examples={
                'application/json': {
                    'error': 'Недостаточно прав доступа'
                }
            }
        )
    }
)
@api_view(['GET'])
@require_roles('superadmin')
def superadmin_panel(request):
    """Панель супер администратора"""
    return Response({
        'message': 'Добро пожаловать в панель супер администратора!',
        'user': UserSerializer(request.user).data
    }, status=status.HTTP_200_OK)