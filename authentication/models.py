from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class SMSVerification(models.Model):
    """Модель для хранения SMS кодов верификации"""
    
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')
    code = models.CharField(max_length=6, verbose_name='Код подтверждения')
    is_used = models.BooleanField(default=False, verbose_name='Использован')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    expires_at = models.DateTimeField(verbose_name='Дата истечения')
    
    class Meta:
        verbose_name = 'SMS верификация'
        verbose_name_plural = 'SMS верификации'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"SMS для {self.phone} - {self.code}"
    
    def is_expired(self):
        """Проверяет, истек ли код"""
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Проверяет, действителен ли код"""
        return not self.is_used and not self.is_expired()


class AuthToken(models.Model):
    """Модель для хранения токенов аутентификации"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    token = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='Токен')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    expires_at = models.DateTimeField(verbose_name='Дата истечения')
    
    class Meta:
        verbose_name = 'Токен аутентификации'
        verbose_name_plural = 'Токены аутентификации'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Токен для {self.user.phone}"
    
    def is_expired(self):
        """Проверяет, истек ли токен"""
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Проверяет, действителен ли токен"""
        return self.is_active and not self.is_expired()