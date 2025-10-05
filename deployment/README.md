# 🚀 Deployment для Django Backend

Этот каталог содержит все необходимые файлы для развертывания Django backend приложения на серверах.

## 📁 Структура

```
deployment/
├── ansible/                 # Ansible конфигурация
│   ├── ansible.cfg         # Настройки Ansible
│   ├── deploy.yml          # Основной playbook
│   ├── deploy.sh           # Скрипт деплоя
│   ├── vault.yml           # Секреты (зашифрованы)
│   ├── Makefile            # Команды для удобства
│   ├── inventory/          # Список серверов
│   ├── group_vars/         # Переменные по группам
│   └── roles/              # Ansible роли
└── README.md               # Этот файл
```

## 🎯 Быстрый старт

### 1. Подготовка серверов

```bash
# Создайте серверы (Ubuntu 20.04+)
# Настройте SSH ключи
ssh-keygen -t rsa -b 4096
ssh-copy-id -i ~/.ssh/id_rsa.pem ubuntu@your-server-ip
```

### 2. Настройка Ansible

```bash
cd deployment/ansible

# Установите Ansible
pip install ansible

# Настройте серверы в inventory/hosts
# Настройте переменные в group_vars/
# Создайте vault с секретами
ansible-vault create vault.yml
```

### 3. Деплой

```bash
# Проверка конфигурации
make check

# Деплой на staging
make staging

# Деплой на production
make production
```

## 🔧 Команды

### Основные команды

```bash
# Проверка
make check                    # Проверить конфигурацию
make ping                     # Проверить подключение
make status                   # Статус сервисов

# Деплой
make staging                  # Деплой на staging
make production               # Деплой на production
make check-staging           # Проверка staging
make check-production        # Проверка production

# Управление
make restart-django          # Перезапустить Django
make restart-nginx           # Перезапустить Nginx
make restart-all             # Перезапустить все
make logs                    # Просмотреть логи

# Обновления
make update-code             # Обновить код
make update-nginx            # Обновить Nginx
make update-db               # Обновить БД

# Vault
make vault-edit              # Редактировать секреты
make vault-view              # Просмотреть секреты
```

### Ручные команды

```bash
# Проверка подключения
ansible production -m ping

# Проверка синтаксиса
ansible-playbook --syntax-check deploy.yml

# Тестовый запуск
./deploy.sh production --check

# Деплой с тегами
./deploy.sh production --tags "nginx,django_app"

# Подробный вывод
./deploy.sh production --verbose
```

## 📋 Настройка

### 1. Inventory (inventory/hosts)

```ini
[production]
your-server-1 ansible_host=1.2.3.4 ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/your-key.pem

[staging]
staging-server ansible_host=5.6.7.8 ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/staging-key.pem
```

### 2. Переменные (group_vars/all.yml)

```yaml
app_name: django_backend
app_repo: "https://github.com/your-username/base-python-back.git"
django_allowed_hosts:
  - "yourdomain.com"
  - "api.yourdomain.com"
```

### 3. Секреты (vault.yml)

```bash
# Создать vault
ansible-vault create vault.yml

# Редактировать
ansible-vault edit vault.yml

# Просмотреть
ansible-vault view vault.yml
```

## 🏗️ Архитектура

### Компоненты

- **Python 3.11** - Runtime для Django
- **PostgreSQL** - База данных
- **Redis** - Кеширование
- **Nginx** - Веб-сервер и прокси
- **Gunicorn** - WSGI сервер
- **Systemd** - Управление сервисами

### Роли

- **python** - Установка Python и виртуального окружения
- **postgresql** - Настройка базы данных
- **redis** - Настройка Redis
- **nginx** - Настройка веб-сервера
- **django_app** - Развертывание Django приложения
- **monitoring** - Мониторинг и логирование
- **backup** - Автоматические бэкапы

## 🔒 Безопасность

### SSH ключи

```bash
# Генерация ключа
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"

# Копирование на сервер
ssh-copy-id -i ~/.ssh/id_rsa.pub ubuntu@your-server-ip
```

### Файрвол

```bash
# Настройка UFW
ansible production -m ufw -a "rule=allow port=22"
ansible production -m ufw -a "rule=allow port=80"
ansible production -m ufw -a "rule=allow port=443"
ansible production -m ufw -a "state=enabled"
```

### SSL сертификаты

```bash
# Автоматическая настройка SSL
make ssl-setup

# Принудительное обновление
make ssl-renew

# Тестирование SSL
make ssl-test

# Ручная настройка
ansible production -m shell -a "certbot --nginx -d yourdomain.com"
```

**SSL автоматически:**
- ✅ Получает сертификаты от Let's Encrypt
- ✅ Продлевает каждые 3 месяца
- ✅ Мониторит срок действия
- ✅ Отправляет email уведомления
- ✅ Настраивает HSTS и безопасность

## 📊 Мониторинг

### Health Check

```bash
# Проверка здоровья
curl http://your-server-ip/health/

# Через Ansible
ansible production -m uri -a "url=http://localhost/health/ return_content=yes"
```

### Логи

```bash
# Логи Django
journalctl -u django -f

# Логи Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

## 🔄 Обновления

### Обновление кода

```bash
# Обновление только кода
make update-code

# Полное обновление
make production
```

### Откат

```bash
# Откат к предыдущей версии
ansible production -m git -a "repo={{ app_repo }} dest={{ app_home }}/app version=previous-commit"
make restart-django
```

## 🐛 Отладка

### Проблемы с подключением

```bash
# Проверка SSH
ssh -i ~/.ssh/your-key.pem ubuntu@your-server-ip

# Проверка Ansible
ansible production -m ping -vvv
```

### Проблемы с конфигурацией

```bash
# Проверка синтаксиса
ansible-playbook --syntax-check deploy.yml

# Проверка переменных
ansible production -m debug -a "var=hostvars[inventory_hostname]"
```

### Проблемы с сервисами

```bash
# Статус сервисов
systemctl status django
systemctl status nginx
systemctl status postgresql

# Логи сервисов
journalctl -u django -f
journalctl -u nginx -f
```

## 📚 Дополнительные ресурсы

- [Ansible Documentation](https://docs.ansible.com/)
- [Django Deployment](https://docs.djangoproject.com/en/stable/howto/deployment/)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [PostgreSQL Administration](https://www.postgresql.org/docs/)
- [Systemd Documentation](https://systemd.io/)

## 🆘 Поддержка

При возникновении проблем:

1. Проверьте логи: `make logs`
2. Проверьте конфигурацию: `make check`
3. Проверьте подключение: `make ping`
4. Проверьте статус: `make status`

## 📝 Changelog

### v1.0.0
- Первоначальная версия
- Поддержка Django + PostgreSQL + Nginx
- Автоматические бэкапы
- Мониторинг и логирование
- SSL поддержка
