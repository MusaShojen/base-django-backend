# 🚀 Quick Start Guide

Быстрый старт для деплоя Django backend с Ansible.

## 📋 Предварительные требования

### На вашей машине:
- Python 3.8+
- Ansible 2.9+
- SSH доступ к серверу

### На сервере:
- Ubuntu 20.04+ или CentOS 8+
- SSH доступ
- Пользователь с sudo правами

## ⚡ Быстрый деплой

### 1. Клонирование репозитория

```bash
git clone https://github.com/yourusername/base-python-back.git
cd base-python-back
```

### 2. Настройка переменных

```bash
# Копируем примеры конфигурации
cp deployment/ansible/group_vars/all.yml.example deployment/ansible/group_vars/all.yml
cp deployment/ansible/group_vars/production.yml.example deployment/ansible/group_vars/production.yml

# Редактируем настройки
nano deployment/ansible/group_vars/all.yml
nano deployment/ansible/group_vars/production.yml
```

### 3. Настройка инвентаря

```bash
# Редактируем список серверов
nano deployment/ansible/inventory/hosts
```

### 4. Деплой

```bash
cd deployment/ansible

# Полный деплой
make production

# Или пошагово
make setup-server
make deploy-app
make setup-nginx
make ssl-setup
```

## 🔧 Настройка для нового проекта

### 1. Форк репозитория

```bash
# Клонируем базовый репозиторий
git clone https://github.com/yourusername/base-python-back.git my-new-project
cd my-new-project

# Удаляем связь с оригинальным репозиторием
git remote remove origin

# Добавляем свой репозиторий
git remote add origin https://github.com/yourusername/my-new-project.git
```

### 2. Настройка проекта

```bash
# Редактируем настройки Django
nano backend/settings.py

# Добавляем свои приложения
python manage.py startapp myapp

# Настраиваем деплой
nano deployment/ansible/group_vars/production.yml
```

### 3. Деплой нового проекта

```bash
cd deployment/ansible
make production
```

## 📁 Структура проекта

```
base-python-back/
├── backend/                 # Django проект
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── authentication/         # Аутентификация
├── users/                  # Пользователи
├── deployment/            # Деплой конфигурация
│   └── ansible/
│       ├── deploy.yml      # Основной плейбук
│       ├── roles/          # Роли Ansible
│       ├── inventory/      # Инвентарь серверов
│       ├── group_vars/     # Переменные
│       └── Makefile        # Команды деплоя
├── requirements.txt
├── Dockerfile
└── README.md
```

## 🛠️ Полезные команды

### Деплой
```bash
make production          # Полный деплой
make staging            # Деплой на staging
make update-app         # Обновить только приложение
make update-nginx       # Обновить только Nginx
make ssl-setup         # Настроить SSL
```

### Мониторинг
```bash
make status            # Статус сервисов
make logs             # Просмотр логов
make backup           # Создать бэкап
make restore          # Восстановить из бэкапа
```

### Отладка
```bash
make check            # Проверка конфигурации
make test             # Тестирование
make debug            # Отладочный режим
```

## 🔐 Безопасность

### Первоначальная настройка

```bash
# Настройка SSH ключей
ssh-copy-id user@your-server

# Настройка файрвола
make setup-firewall

# Настройка SSL
make ssl-setup
```

### Регулярное обслуживание

```bash
# Обновление системы
make update-system

# Обновление SSL
make ssl-renew

# Создание бэкапов
make backup
```

## 📊 Мониторинг

### Health Check

```bash
# Проверка статуса
curl https://yourdomain.com/health/

# Проверка API
curl https://yourdomain.com/api/auth/profile/

# Проверка Swagger
curl https://yourdomain.com/swagger/
```

### Логи

```bash
# Логи приложения
tail -f /opt/django_backend/logs/django.log

# Логи Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Логи системы
journalctl -u django_backend -f
```

## 🆘 Устранение проблем

### Частые проблемы

1. **Ошибка подключения SSH**
   ```bash
   # Проверить SSH ключи
   ssh -T user@your-server
   
   # Проверить инвентарь
   ansible production -m ping
   ```

2. **Ошибка прав доступа**
   ```bash
   # Проверить пользователя
   ansible production -m shell -a "whoami"
   
   # Проверить sudo права
   ansible production -m shell -a "sudo whoami"
   ```

3. **Ошибка базы данных**
   ```bash
   # Проверить PostgreSQL
   ansible production -m shell -a "sudo systemctl status postgresql"
   
   # Проверить подключение
   ansible production -m shell -a "sudo -u postgres psql -c '\\l'"
   ```

### Отладка

```bash
# Подробный вывод
ansible-playbook deploy.yml -vvv

# Проверка синтаксиса
ansible-playbook deploy.yml --syntax-check

# Тестовый запуск
ansible-playbook deploy.yml --check
```

## 📚 Дополнительные ресурсы

- [Ansible документация](https://docs.ansible.com/)
- [Django деплой](https://docs.djangoproject.com/en/stable/howto/deployment/)
- [Nginx конфигурация](https://nginx.org/en/docs/)
- [SSL с Let's Encrypt](https://letsencrypt.org/)

## 🤝 Поддержка

Если у вас есть вопросы или проблемы:

1. Проверьте [FAQ](FAQ.md)
2. Посмотрите [логи](LOGS.md)
3. Создайте [issue](https://github.com/yourusername/base-python-back/issues)

---

**Удачного деплоя! 🚀**
