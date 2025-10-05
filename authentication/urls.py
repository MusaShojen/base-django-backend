from django.urls import path
from . import views

urlpatterns = [
    # Основные OTP endpoints
    path('send-code/', views.send_verification_code, name='send_verification_code'),
    path('verify-code/', views.verify_code, name='verify_code'),
    
    # Telegram и SMS fallback
    path('send-sms-fallback/', views.send_sms_fallback, name='send_sms_fallback'),
    path('check-telegram/', views.check_telegram_availability, name='check_telegram_availability'),
    path('balance-info/', views.get_balance_info, name='get_balance_info'),
    
    # Аутентификация
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Профиль пользователя
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    
    # Защищенные роуты с разными ролями
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('admin/', views.admin_panel, name='admin_panel'),
    path('superadmin/', views.superadmin_panel, name='superadmin_panel'),
]
