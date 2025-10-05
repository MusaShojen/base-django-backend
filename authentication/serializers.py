from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import SMSVerification, AuthToken
from .validators import validate_phone_number, normalize_phone_number

User = get_user_model()


class PhoneVerificationSerializer(serializers.Serializer):
    """Сериализатор для запроса SMS кода"""
    phone = serializers.CharField(max_length=20, help_text='Номер телефона в международном формате E.164 (например: +1234567890)')
    is_reset = serializers.BooleanField(default=False, help_text='Флаг для восстановления пароля')
    
    def validate_phone(self, value):
        """Валидация номера телефона"""
        try:
            # Нормализуем номер
            normalized_phone = normalize_phone_number(value)
            return normalized_phone
        except Exception as e:
            raise serializers.ValidationError(
                'Номер телефона должен быть в международном формате E.164 '
                '(например: +1234567890, +79123456789). '
                f'Ошибка: {str(e)}'
            )
    


class CodeVerificationSerializer(serializers.Serializer):
    """Сериализатор для проверки SMS кода"""
    phone = serializers.CharField(max_length=20, help_text='Номер телефона в международном формате E.164')
    code = serializers.CharField(max_length=6, help_text='Код подтверждения')
    
    def validate_phone(self, value):
        """Валидация номера телефона"""
        try:
            # Нормализуем номер
            normalized_phone = normalize_phone_number(value)
            return normalized_phone
        except Exception as e:
            raise serializers.ValidationError(
                'Номер телефона должен быть в международном формате E.164 '
                '(например: +1234567890, +79123456789). '
                f'Ошибка: {str(e)}'
            )
    
    def validate_code(self, value):
        """Валидация кода"""
        if not value.isdigit():
            raise serializers.ValidationError("Код должен содержать только цифры")
        if len(value) != 6:
            raise serializers.ValidationError("Код должен содержать 6 цифр")
        return value


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя (без пароля)"""
    
    class Meta:
        model = User
        fields = ['phone', 'username', 'email', 'first_name', 'last_name']
        extra_kwargs = {
            'phone': {'required': True},
            'username': {'required': True},
            'email': {'required': True},
        }
    
    def validate_phone(self, value):
        """Проверка уникальности номера телефона"""
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Пользователь с таким номером телефона уже существует")
        return value
    
    def create(self, validated_data):
        """Создание пользователя без пароля"""
        user = User.objects.create_user(
            **validated_data,
            should_update_password=True,
            is_active=False,  # Неактивен до установки пароля
            is_phone_verified=True  # Номер уже подтвержден
        )
        return user


class CompleteRegistrationSerializer(serializers.Serializer):
    """Сериализатор для завершения регистрации"""
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6)
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    
    def validate_phone(self, value):
        """Валидация номера телефона"""
        try:
            normalized_phone = normalize_phone_number(value)
            return normalized_phone
        except Exception as e:
            raise serializers.ValidationError(
                'Номер телефона должен быть в международном формате E.164 '
                f'Ошибка: {str(e)}'
            )
    
    def validate_code(self, value):
        """Валидация кода"""
        if not value.isdigit():
            raise serializers.ValidationError("Код должен содержать только цифры")
        if len(value) != 6:
            raise serializers.ValidationError("Код должен содержать 6 цифр")
        return value


class SetPasswordSerializer(serializers.Serializer):
    """Сериализатор для установки пароля"""
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(min_length=8, write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Валидация данных"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        return attrs
    
    def validate_phone(self, value):
        """Валидация номера телефона"""
        try:
            normalized_phone = normalize_phone_number(value)
            return normalized_phone
        except Exception as e:
            raise serializers.ValidationError(
                'Номер телефона должен быть в международном формате E.164 '
                f'Ошибка: {str(e)}'
            )


class ResetPasswordSerializer(serializers.Serializer):
    """Сериализатор для восстановления пароля"""
    phone = serializers.CharField(max_length=20)
    
    def validate_phone(self, value):
        """Валидация номера телефона"""
        try:
            normalized_phone = normalize_phone_number(value)
            return normalized_phone
        except Exception as e:
            raise serializers.ValidationError(
                'Номер телефона должен быть в международном формате E.164 '
                f'Ошибка: {str(e)}'
            )


class UserLoginSerializer(serializers.Serializer):
    """Сериализатор для входа пользователя"""
    phone = serializers.CharField(max_length=20, help_text='Номер телефона')
    password = serializers.CharField(write_only=True, help_text='Пароль')


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения информации о пользователе"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    should_update_password = serializers.BooleanField(read_only=True)
    is_registration_complete = serializers.BooleanField(source='is_registration_complete', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'phone', 'username', 'email', 'first_name', 'last_name', 
                 'role', 'role_display', 'is_phone_verified', 'should_update_password',
                 'is_registration_complete', 'registration_completed_at', 'created_at']
        read_only_fields = ['id', 'created_at', 'registration_completed_at']


class TokenSerializer(serializers.ModelSerializer):
    """Сериализатор для токена аутентификации"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = AuthToken
        fields = ['token', 'user', 'created_at', 'expires_at']
        read_only_fields = ['token', 'created_at', 'expires_at']
