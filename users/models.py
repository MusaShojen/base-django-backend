from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Расширенная модель пользователя с ролями"""
    
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('admin', 'Администратор'),
        ('superadmin', 'Супер администратор'),
    ]
    
    phone = models.CharField(max_length=20, unique=True, verbose_name='Номер телефона')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user', verbose_name='Роль')
    is_phone_verified = models.BooleanField(default=False, verbose_name='Телефон подтвержден')
    should_update_password = models.BooleanField(default=True, verbose_name='Требуется обновление пароля')
    registration_completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата завершения регистрации')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['username', 'email']
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return f"{self.phone} ({self.get_role_display()})"
    
    def has_role(self, role):
        """Проверяет, есть ли у пользователя указанная роль"""
        return self.role == role
    
    def has_any_role(self, roles):
        """Проверяет, есть ли у пользователя любая из указанных ролей"""
        return self.role in roles
    
    def is_admin(self):
        """Проверяет, является ли пользователь администратором"""
        return self.role in ['admin', 'superadmin']
    
    def is_superadmin(self):
        """Проверяет, является ли пользователь супер администратором"""
        return self.role == 'superadmin'
    
    def is_registration_complete(self):
        """Проверяет, завершена ли регистрация пользователя"""
        return not self.should_update_password and self.is_active and self.is_phone_verified
    
    def can_use_service(self):
        """Проверяет, может ли пользователь пользоваться сервисом"""
        return self.is_registration_complete()
    
    def complete_registration(self):
        """Завершает регистрацию пользователя"""
        from django.utils import timezone
        self.should_update_password = False
        self.is_active = True
        self.is_phone_verified = True
        self.registration_completed_at = timezone.now()
        self.save()