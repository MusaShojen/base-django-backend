"""
Универсальный OTP сервис с поддержкой Telegram и SMS
"""
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import SMSVerification
from .services import GreenSMSService
from .telegram_service import TelegramGatewayService
from .cache_utils import RateLimiter, SMSVerificationCache


class UniversalOTPService:
    """Универсальный сервис для отправки OTP кодов через Telegram или SMS"""
    
    def __init__(self):
        self.telegram_service = TelegramGatewayService()
        self.sms_service = GreenSMSService()
    
    def send_verification_code(self, phone, prefer_telegram=True):
        """
        Отправляет код верификации
        
        Args:
            phone: Номер телефона
            prefer_telegram: Предпочитать Telegram (True) или SMS (False)
        
        Returns:
            dict: {
                'success': bool,
                'method': 'telegram' | 'sms' | 'none',
                'message': str,
                'sms_verification': SMSVerification | None,
                'telegram_available': bool,
                'fallback_required': bool
            }
        """
        # Проверяем rate limiting
        if not RateLimiter.check_rate_limit(phone, limit=5, window=3600):
            return {
                'success': False,
                'method': 'none',
                'message': 'Превышен лимит запросов. Попробуйте позже.',
                'sms_verification': None,
                'telegram_available': False,
                'fallback_required': False
            }
        
        # Проверяем количество попыток
        if not SMSVerificationCache.increment_attempts(phone, max_attempts=5):
            return {
                'success': False,
                'method': 'none',
                'message': 'Превышено максимальное количество попыток. Попробуйте через час.',
                'sms_verification': None,
                'telegram_available': False,
                'fallback_required': False
            }
        
        # Проверяем доступность Telegram
        telegram_available = self.telegram_service.is_telegram_available(phone)
        
        # Логика выбора метода
        if prefer_telegram and telegram_available:
            # Пробуем Telegram
            result = self._send_telegram_code(phone)
            if result['success']:
                return {
                    'success': True,
                    'method': 'telegram',
                    'message': 'Код отправлен в Telegram',
                    'sms_verification': result['sms_verification'],
                    'telegram_available': True,
                    'fallback_required': False
                }
            else:
                # Telegram не сработал, пробуем SMS
                return self._send_sms_code(phone, telegram_failed=True)
        
        elif not prefer_telegram or not telegram_available:
            # Пробуем SMS
            return self._send_sms_code(phone, telegram_available=telegram_available)
        
        else:
            # Telegram недоступен, отправляем SMS
            return self._send_sms_code(phone, telegram_available=False)
    
    def _send_telegram_code(self, phone):
        """Отправляет код через Telegram"""
        try:
            sms_verification = self.telegram_service.send_otp_code(phone)
            if sms_verification:
                return {
                    'success': True,
                    'sms_verification': sms_verification
                }
        except Exception as e:
            print(f"Ошибка отправки Telegram OTP: {e}")
        
        return {
            'success': False,
            'sms_verification': None
        }
    
    def _send_sms_code(self, phone, telegram_available=False, telegram_failed=False):
        """Отправляет код через SMS"""
        try:
            sms_verification = self.sms_service.send_verification_code(phone)
            if sms_verification:
                message = "Код отправлен по SMS"
                if telegram_failed:
                    message = "Telegram недоступен. Код отправлен по SMS"
                elif not telegram_available:
                    message = "Код отправлен по SMS"
                
                return {
                    'success': True,
                    'method': 'sms',
                    'message': message,
                    'sms_verification': sms_verification,
                    'telegram_available': telegram_available,
                    'fallback_required': False
                }
        except Exception as e:
            print(f"Ошибка отправки SMS: {e}")
        
        return {
            'success': False,
            'method': 'none',
            'message': 'Ошибка отправки кода',
            'sms_verification': None,
            'telegram_available': telegram_available,
            'fallback_required': False
        }
    
    def verify_code(self, phone, code):
        """Проверяет код верификации"""
        try:
            sms_verification = SMSVerification.objects.get(
                phone=phone,
                code=code,
                is_used=False
            )
            
            if not sms_verification.is_valid():
                return False
            
            # Если есть request_id, проверяем через Telegram
            if sms_verification.request_id:
                telegram_valid = self.telegram_service.verify_otp_code(phone, code)
                if telegram_valid:
                    sms_verification.is_used = True
                    sms_verification.save()
                    return True
            
            # Проверяем через SMS сервис
            sms_valid = self.sms_service.verify_code(phone, code)
            if sms_valid:
                sms_verification.is_used = True
                sms_verification.save()
                return True
            
            return False
            
        except SMSVerification.DoesNotExist:
            return False
    
    def send_sms_fallback(self, phone):
        """Отправляет SMS как резервный вариант"""
        try:
            sms_verification = self.sms_service.send_verification_code(phone)
            if sms_verification:
                return {
                    'success': True,
                    'message': 'Код отправлен по SMS',
                    'sms_verification': sms_verification
                }
        except Exception as e:
            print(f"Ошибка отправки SMS fallback: {e}")
        
        return {
            'success': False,
            'message': 'Ошибка отправки SMS',
            'sms_verification': None
        }
    
    def check_telegram_availability(self, phone):
        """Проверяет доступность Telegram для номера"""
        return self.telegram_service.is_telegram_available(phone)
    
    def get_delivery_status(self, request_id):
        """Получает статус доставки"""
        if not request_id:
            return 'no_request_id'
        
        # Пробуем Telegram
        telegram_status = self.telegram_service.get_delivery_status(request_id)
        if telegram_status != 'unknown':
            return telegram_status
        
        # Пробуем SMS
        sms_status = self.sms_service.get_sms_status(request_id)
        return sms_status
    
    def get_balance_info(self):
        """Получает информацию о балансах"""
        return {
            'telegram_available': settings.TELEGRAM_GATEWAY_ENABLED,
            'sms_balance': self.sms_service.get_balance() if hasattr(self.sms_service, 'get_balance') else None
        }
