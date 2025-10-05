"""
Telegram Gateway API сервис для отправки OTP кодов
"""
import requests
import json
import hashlib
import hmac
import time
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import SMSVerification


class TelegramGatewayService:
    """Сервис для работы с Telegram Gateway API"""
    
    def __init__(self):
        self.token = settings.TELEGRAM_GATEWAY_TOKEN
        self.base_url = settings.TELEGRAM_GATEWAY_URL
        self.debug_mode = settings.TELEGRAM_GATEWAY_DEBUG
        self.enabled = settings.TELEGRAM_GATEWAY_ENABLED
    
    def _make_request(self, method, params=None):
        """Выполняет запрос к Telegram Gateway API"""
        if self.debug_mode:
            print(f"DEBUG Telegram Gateway: {method} - {params}")
            return self._mock_response(method, params)
        
        if not self.enabled or not self.token:
            return None
        
        url = f"{self.base_url}/{method}"
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, json=params, headers=headers, timeout=10)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Ошибка Telegram Gateway API: {e}")
            return None
    
    def _mock_response(self, method, params):
        """Мок ответ для debug режима"""
        if method == 'checkSendAbility':
            return {
                'ok': True,
                'result': {
                    'request_id': f'debug_request_{int(time.time())}',
                    'phone_number': params.get('phone_number'),
                    'request_cost': 0.0,
                    'remaining_balance': 100.0
                }
            }
        elif method == 'sendVerificationMessage':
            return {
                'ok': True,
                'result': {
                    'request_id': f'debug_request_{int(time.time())}',
                    'phone_number': params.get('phone_number'),
                    'request_cost': 0.0,
                    'remaining_balance': 100.0,
                    'delivery_status': {
                        'status': 'sent',
                        'updated_at': int(time.time())
                    }
                }
            }
        elif method == 'checkVerificationStatus':
            return {
                'ok': True,
                'result': {
                    'request_id': params.get('request_id'),
                    'phone_number': '+1234567890',
                    'delivery_status': {
                        'status': 'delivered',
                        'updated_at': int(time.time())
                    },
                    'verification_status': {
                        'status': 'code_valid' if params.get('code') == '123456' else 'code_invalid',
                        'updated_at': int(time.time())
                    }
                }
            }
        return None
    
    def check_send_ability(self, phone_number):
        """Проверяет возможность отправки OTP в Telegram"""
        params = {
            'phone_number': phone_number
        }
        
        response = self._make_request('checkSendAbility', params)
        
        if response and response.get('ok'):
            return response['result']
        return None
    
    def send_verification_message(self, phone_number, code=None, code_length=6, request_id=None):
        """Отправляет OTP код через Telegram"""
        params = {
            'phone_number': phone_number,
            'code_length': code_length,
            'ttl': 300  # 5 минут
        }
        
        if code:
            params['code'] = code
        if request_id:
            params['request_id'] = request_id
        
        response = self._make_request('sendVerificationMessage', params)
        
        if response and response.get('ok'):
            return response['result']
        return None
    
    def check_verification_status(self, request_id, code=None):
        """Проверяет статус верификации и валидность кода"""
        params = {
            'request_id': request_id
        }
        
        if code:
            params['code'] = code
        
        response = self._make_request('checkVerificationStatus', params)
        
        if response and response.get('ok'):
            return response['result']
        return None
    
    def revoke_verification_message(self, request_id):
        """Отзывает OTP сообщение"""
        params = {
            'request_id': request_id
        }
        
        response = self._make_request('revokeVerificationMessage', params)
        
        if response and response.get('ok'):
            return response['result']
        return None
    
    def send_otp_code(self, phone_number):
        """Отправляет OTP код через Telegram (основной метод)"""
        # Сначала проверяем возможность отправки
        ability_check = self.check_send_ability(phone_number)
        
        if not ability_check:
            return None
        
        # Генерируем код
        code = self._generate_code()
        
        # Отправляем OTP
        result = self.send_verification_message(
            phone_number=phone_number,
            code=code,
            request_id=ability_check.get('request_id')
        )
        
        if result:
            # Сохраняем в базу данных
            expires_at = timezone.now() + timedelta(minutes=5)
            
            # Деактивируем предыдущие коды
            SMSVerification.objects.filter(phone=phone_number, is_used=False).update(is_used=True)
            
            # Создаем новую запись
            sms_verification = SMSVerification.objects.create(
                phone=phone_number,
                code=code,
                request_id=result.get('request_id'),
                expires_at=expires_at
            )
            
            return sms_verification
        
        return None
    
    def verify_otp_code(self, phone_number, code):
        """Проверяет OTP код через Telegram"""
        try:
            sms_verification = SMSVerification.objects.get(
                phone=phone_number,
                code=code,
                is_used=False
            )
            
            if not sms_verification.is_valid():
                return False
            
            # Проверяем через Telegram API
            if sms_verification.request_id:
                status = self.check_verification_status(
                    sms_verification.request_id, 
                    code
                )
                
                if status and status.get('verification_status', {}).get('status') == 'code_valid':
                    sms_verification.is_used = True
                    sms_verification.save()
                    return True
            
            return False
            
        except SMSVerification.DoesNotExist:
            return False
    
    def _generate_code(self):
        """Генерирует 6-значный код"""
        import random
        return str(random.randint(100000, 999999))
    
    def get_delivery_status(self, request_id):
        """Получает статус доставки"""
        status = self.check_verification_status(request_id)
        
        if status and status.get('delivery_status'):
            return status['delivery_status'].get('status')
        
        return 'unknown'
    
    def is_telegram_available(self, phone_number):
        """Проверяет, доступен ли Telegram для номера"""
        if not self.enabled:
            return False
        
        ability = self.check_send_ability(phone_number)
        return ability is not None
