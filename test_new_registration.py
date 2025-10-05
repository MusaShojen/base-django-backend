#!/usr/bin/env python3
"""
Тестовый скрипт для новой системы многоэтапной регистрации
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_new_registration_flow():
    """Тестирует новый процесс регистрации"""
    print("🧪 Тестирование новой системы многоэтапной регистрации")
    print("=" * 60)
    
    # Тестовые данные
    phone = "+79999999999"
    username = "test_user"
    email = "test@example.com"
    first_name = "Test"
    last_name = "User"
    password = "testpassword123"
    
    # Шаг 1: Отправка кода для регистрации
    print("\n📱 Шаг 1: Отправка кода для регистрации")
    response = requests.post(f"{BASE_URL}/api/auth/send-code/", json={
        "phone": phone,
        "is_reset": False
    })
    
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code != 200:
        print("❌ Ошибка на шаге 1")
        return
    
    # Шаг 2: Завершение регистрации (создание пользователя без пароля)
    print("\n👤 Шаг 2: Завершение регистрации")
    response = requests.post(f"{BASE_URL}/api/auth/complete-registration/", json={
        "phone": phone,
        "code": "123456",  # В debug режиме всегда 123456
        "username": username,
        "email": email,
        "first_name": first_name,
        "last_name": last_name
    })
    
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code != 201:
        print("❌ Ошибка на шаге 2")
        return
    
    user_data = response.json()["user"]
    print(f"✅ Пользователь создан с should_update_password: {user_data['should_update_password']}")
    
    # Шаг 3: Установка пароля
    print("\n🔐 Шаг 3: Установка пароля")
    response = requests.post(f"{BASE_URL}/api/auth/set-password/", json={
        "phone": phone,
        "password": password,
        "password_confirm": password
    })
    
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code != 200:
        print("❌ Ошибка на шаге 3")
        return
    
    token = response.json()["token"]
    user_data = response.json()["user"]
    print(f"✅ Регистрация завершена! should_update_password: {user_data['should_update_password']}")
    print(f"🔑 Токен: {token}")
    
    # Шаг 4: Тестирование входа
    print("\n🚪 Шаг 4: Тестирование входа")
    response = requests.post(f"{BASE_URL}/api/auth/login/", json={
        "phone": phone,
        "password": password
    })
    
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        print("✅ Вход выполнен успешно!")
    else:
        print("❌ Ошибка входа")
    
    return token


def test_password_reset_flow():
    """Тестирует процесс восстановления пароля"""
    print("\n\n🔄 Тестирование восстановления пароля")
    print("=" * 60)
    
    phone = "+79999999999"
    new_password = "newpassword123"
    
    # Шаг 1: Запрос на восстановление пароля
    print("\n📱 Шаг 1: Запрос на восстановление пароля")
    response = requests.post(f"{BASE_URL}/api/auth/reset-password/", json={
        "phone": phone
    })
    
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code != 200:
        print("❌ Ошибка на шаге 1 восстановления")
        return
    
    # Шаг 2: Установка нового пароля
    print("\n🔐 Шаг 2: Установка нового пароля")
    response = requests.post(f"{BASE_URL}/api/auth/set-new-password/", json={
        "phone": phone,
        "password": new_password,
        "password_confirm": new_password,
        "code": "123456"  # В debug режиме всегда 123456
    })
    
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        print("✅ Пароль успешно изменен!")
        token = response.json()["token"]
        return token
    else:
        print("❌ Ошибка установки нового пароля")
        return None


def test_protection_against_spam():
    """Тестирует защиту от спама при регистрации"""
    print("\n\n🛡️ Тестирование защиты от спама")
    print("=" * 60)
    
    phone = "+79999999999"
    
    # Попытка зарегистрировать уже существующий номер без is_reset
    print("\n🚫 Попытка повторной регистрации без is_reset")
    response = requests.post(f"{BASE_URL}/api/auth/send-code/", json={
        "phone": phone,
        "is_reset": False
    })
    
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 400:
        print("✅ Защита от спама работает!")
    else:
        print("❌ Защита от спама не работает")


if __name__ == "__main__":
    try:
        # Тестируем новую регистрацию
        token = test_new_registration_flow()
        
        if token:
            # Тестируем восстановление пароля
            test_password_reset_flow()
            
            # Тестируем защиту от спама
            test_protection_against_spam()
        
        print("\n🎉 Все тесты завершены!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения. Убедитесь, что сервер запущен на localhost:8000")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
