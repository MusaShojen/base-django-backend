from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import SMSVerification, AuthToken

User = get_user_model()


class PhoneVerificationSerializer(serializers.Serializer):
    """Сериализатор для запроса SMS кода"""
    phone = serializers.CharField(max_length=20, help_text='Номер телефона')
    
    def validate_phone(self, value):
        """Валидация номера телефона"""
        # Простая валидация - можно расширить
        if not value.startswith('+'):
            raise serializers.ValidationError("Номер телефона должен начинаться с '+'")
        if len(value) < 10:
            raise serializers.ValidationError("Номер телефона слишком короткий")
        return value


class CodeVerificationSerializer(serializers.Serializer):
    """Сериализатор для проверки SMS кода"""
    phone = serializers.CharField(max_length=20, help_text='Номер телефона')
    code = serializers.CharField(max_length=6, help_text='Код подтверждения')
    
    def validate_code(self, value):
        """Валидация кода"""
        if not value.isdigit():
            raise serializers.ValidationError("Код должен содержать только цифры")
        if len(value) != 6:
            raise serializers.ValidationError("Код должен содержать 6 цифр")
        return value


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['phone', 'username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']
        extra_kwargs = {
            'phone': {'required': True},
            'username': {'required': True},
            'email': {'required': True},
        }
    
    def validate(self, attrs):
        """Валидация данных"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        return attrs
    
    def validate_phone(self, value):
        """Проверка уникальности номера телефона"""
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Пользователь с таким номером телефона уже существует")
        return value
    
    def create(self, validated_data):
        """Создание пользователя"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """Сериализатор для входа пользователя"""
    phone = serializers.CharField(max_length=20, help_text='Номер телефона')
    password = serializers.CharField(write_only=True, help_text='Пароль')


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения информации о пользователе"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'phone', 'username', 'email', 'first_name', 'last_name', 
                 'role', 'role_display', 'is_phone_verified', 'created_at']
        read_only_fields = ['id', 'created_at']


class TokenSerializer(serializers.ModelSerializer):
    """Сериализатор для токена аутентификации"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = AuthToken
        fields = ['token', 'user', 'created_at', 'expires_at']
        read_only_fields = ['token', 'created_at', 'expires_at']
