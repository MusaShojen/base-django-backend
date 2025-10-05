from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from authentication.decorators import require_roles
from authentication.serializers import UserSerializer

User = get_user_model()


@swagger_auto_schema(
    method='get',
    operation_summary='Список всех пользователей',
    operation_description='Возвращает список всех пользователей в системе (только для администраторов)',
    responses={
        200: openapi.Response(
            description='Список пользователей',
            examples={
                'application/json': {
                    'users': [
                        {
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
                    ],
                    'count': 1
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
def user_list(request):
    """Список всех пользователей (только для админов)"""
    users = User.objects.all().order_by('-created_at')
    serializer = UserSerializer(users, many=True)
    
    return Response({
        'users': serializer.data,
        'count': users.count()
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_summary='Детальная информация о пользователе',
    operation_description='Возвращает подробную информацию о конкретном пользователе (только для администраторов)',
    responses={
        200: openapi.Response(
            description='Информация о пользователе',
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
        ),
        403: openapi.Response(
            description='Недостаточно прав доступа',
            examples={
                'application/json': {
                    'error': 'Недостаточно прав доступа'
                }
            }
        ),
        404: openapi.Response(
            description='Пользователь не найден',
            examples={
                'application/json': {
                    'error': 'Пользователь не найден'
                }
            }
        )
    }
)
@api_view(['GET'])
@require_roles('admin', 'superadmin')
def user_detail(request, user_id):
    """Детальная информация о пользователе (только для админов)"""
    try:
        user = User.objects.get(id=user_id)
        serializer = UserSerializer(user)
        
        return Response({
            'user': serializer.data
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'error': 'Пользователь не найден'
        }, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method='put',
    operation_summary='Изменение роли пользователя',
    operation_description='Изменяет роль пользователя в системе (только для администраторов)',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'role': openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=['user', 'admin', 'superadmin'],
                description='Новая роль пользователя'
            )
        },
        required=['role']
    ),
    responses={
        200: openapi.Response(
            description='Роль пользователя обновлена',
            examples={
                'application/json': {
                    'message': 'Роль пользователя обновлена',
                    'user': {
                        'id': 1,
                        'phone': '+1234567890',
                        'username': 'john_doe',
                        'email': 'john@example.com',
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'role': 'admin',
                        'role_display': 'Администратор',
                        'is_phone_verified': True,
                        'created_at': '2025-01-05T08:00:00Z'
                    }
                }
            }
        ),
        400: openapi.Response(
            description='Неверная роль',
            examples={
                'application/json': {
                    'error': 'Неверная роль'
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
                    'error': 'Недостаточно прав для изменения роли суперадмина'
                }
            }
        ),
        404: openapi.Response(
            description='Пользователь не найден',
            examples={
                'application/json': {
                    'error': 'Пользователь не найден'
                }
            }
        )
    }
)
@api_view(['PUT'])
@require_roles('admin', 'superadmin')
def update_user_role(request, user_id):
    """Изменение роли пользователя (только для админов)"""
    try:
        user = User.objects.get(id=user_id)
        new_role = request.data.get('role')
        
        if new_role not in ['user', 'admin', 'superadmin']:
            return Response({
                'error': 'Неверная роль'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Суперадмин не может изменить роль другого суперадмина
        if user.role == 'superadmin' and request.user.role != 'superadmin':
            return Response({
                'error': 'Недостаточно прав для изменения роли суперадмина'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user.role = new_role
        user.save()
        
        return Response({
            'message': 'Роль пользователя обновлена',
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'error': 'Пользователь не найден'
        }, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method='delete',
    operation_summary='Удаление пользователя',
    operation_description='Удаляет пользователя из системы (только для суперадминистраторов)',
    responses={
        200: openapi.Response(
            description='Пользователь удален',
            examples={
                'application/json': {
                    'message': 'Пользователь удален'
                }
            }
        ),
        400: openapi.Response(
            description='Нельзя удалить самого себя',
            examples={
                'application/json': {
                    'error': 'Нельзя удалить самого себя'
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
        ),
        404: openapi.Response(
            description='Пользователь не найден',
            examples={
                'application/json': {
                    'error': 'Пользователь не найден'
                }
            }
        )
    }
)
@api_view(['DELETE'])
@require_roles('superadmin')
def delete_user(request, user_id):
    """Удаление пользователя (только для суперадмина)"""
    try:
        user = User.objects.get(id=user_id)
        
        # Нельзя удалить самого себя
        if user == request.user:
            return Response({
                'error': 'Нельзя удалить самого себя'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.delete()
        
        return Response({
            'message': 'Пользователь удален'
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'error': 'Пользователь не найден'
        }, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method='get',
    operation_summary='Статистика пользователей',
    operation_description='Возвращает статистику по пользователям системы (только для администраторов)',
    responses={
        200: openapi.Response(
            description='Статистика пользователей',
            examples={
                'application/json': {
                    'total_users': 100,
                    'verified_users': 95,
                    'admin_users': 5,
                    'role_stats': {
                        'user': 90,
                        'admin': 4,
                        'superadmin': 1
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
def user_stats(request):
    """Статистика пользователей (только для админов)"""
    total_users = User.objects.count()
    verified_users = User.objects.filter(is_phone_verified=True).count()
    admin_users = User.objects.filter(role__in=['admin', 'superadmin']).count()
    
    role_stats = {}
    for role, display_name in User.ROLE_CHOICES:
        role_stats[role] = User.objects.filter(role=role).count()
    
    return Response({
        'total_users': total_users,
        'verified_users': verified_users,
        'admin_users': admin_users,
        'role_stats': role_stats
    }, status=status.HTTP_200_OK)