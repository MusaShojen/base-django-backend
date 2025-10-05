import random
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import SMSVerification
from greensms.client import GreenSMS
from .telegram_service import TelegramGatewayService


class GreenSMSService:
    """Сервис для работы с Green SMS API через официальную библиотеку"""
    
    def __init__(self):
        self.user = settings.GREEN_SMS_USER
        self.password = settings.GREEN_SMS_PASSWORD
        self.debug_mode = settings.GREEN_SMS_DEBUG
        
        # Инициализируем клиент только если не в debug режиме
        if not self.debug_mode:
            self.client = GreenSMS(user=self.user, password=self.password)
        else:
            self.client = None
    
    def send_sms(self, phone, message):
        """Отправляет SMS сообщение"""
        if self.debug_mode:
            # В режиме дебага не отправляем реальные SMS
            print(f"DEBUG SMS: {phone} - {message}")
            return True, "debug_request_id"
        
        try:
            # Используем официальную библиотеку GreenSMS
            response = self.client.sms.send(to=phone, txt=message)
            
            if response and hasattr(response, 'request_id'):
                return True, response.request_id
            else:
                return False, None
                
        except Exception as e:
            print(f"Ошибка отправки SMS: {e}")
            return False, None
    
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
        success, request_id = self.send_sms(phone, message)
        
        if success:
            # Сохраняем request_id для отслеживания
            if request_id:
                sms_verification.request_id = request_id
                sms_verification.save()
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
    
    def get_sms_status(self, request_id):
        """Получает статус отправки SMS"""
        if self.debug_mode:
            return "delivered"  # В debug режиме всегда доставлено
        
        try:
            response = self.client.sms.status(request_id=request_id)
            return response.status if response else "unknown"
        except Exception as e:
            print(f"Ошибка получения статуса SMS: {e}")
            return "error"
    
    def get_balance(self):
        """Получает баланс аккаунта"""
        if self.debug_mode:
            return 100.0  # В debug режиме возвращаем тестовый баланс
        
        try:
            response = self.client.account.balance()
            return response.balance if response else 0.0
        except Exception as e:
            print(f"Ошибка получения баланса: {e}")
            return 0.0
