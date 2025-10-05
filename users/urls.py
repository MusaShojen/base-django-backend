from django.urls import path
from . import views

urlpatterns = [
    # Управление пользователями (только для админов)
    path('', views.user_list, name='user_list'),
    path('<int:user_id>/', views.user_detail, name='user_detail'),
    path('<int:user_id>/role/', views.update_user_role, name='update_user_role'),
    path('<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('stats/', views.user_stats, name='user_stats'),
]
