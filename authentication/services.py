import requests
import random
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import SMSVerification


class GreenSMSService:
    """Сервис для работы с Green SMS API"""
    
    def __init__(self):
        self.api_url = settings.GREEN_SMS_API_URL
        self.api_token = settings.GREEN_SMS_API_TOKEN
        self.debug_mode = settings.GREEN_SMS_DEBUG
    
    def send_sms(self, phone, message):
        """Отправляет SMS сообщение"""
        if self.debug_mode:
            # В режиме дебага не отправляем реальные SMS
            print(f"DEBUG SMS: {phone} - {message}")
            return True
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'phone': phone,
                'message': message
            }
            
            response = requests.post(
                f"{self.api_url}/send",
                json=data,
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Ошибка отправки SMS: {e}")
            return False
    
    def generate_verification_code(self):
        """Генерирует 6-значный код подтверждения"""
        return str(random.randint(100000, 999999))
    
    def send_verification_code(self, phone):
        """Отправляет код подтверждения на телефон"""
        code = self.generate_verification_code()
        
        # Сохраняем код в базе данных
        expires_at = timezone.now() + timedelta(minutes=5)  # Код действует 5 минут
        
        # Деактивируем предыдущие коды для этого номера
        SMSVerification.objects.filter(phone=phone, is_used=False).update(is_used=True)
        
        # Создаем новый код
        sms_verification = SMSVerification.objects.create(
            phone=phone,
            code=code,
            expires_at=expires_at
        )
        
        # Отправляем SMS
        message = f"Ваш код подтверждения: {code}"
        success = self.send_sms(phone, message)
        
        if success:
            return sms_verification
        else:
            sms_verification.delete()
            return None
    
    def verify_code(self, phone, code):
        """Проверяет код подтверждения"""
        try:
            sms_verification = SMSVerification.objects.get(
                phone=phone,
                code=code,
                is_used=False
            )
            
            if sms_verification.is_valid():
                sms_verification.is_used = True
                sms_verification.save()
                return True
            else:
                return False
                
        except SMSVerification.DoesNotExist:
            return False
