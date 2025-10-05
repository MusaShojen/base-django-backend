# Ansible Deployment для Django Backend

Этот каталог содержит Ansible playbooks и роли для автоматического развертывания Django backend приложения.

## 📁 Структура

```
deployment/ansible/
├── ansible.cfg              # Конфигурация Ansible
├── deploy.yml               # Основной playbook
├── deploy.sh                # Скрипт для деплоя
├── vault.yml                # Секреты (зашифрованы)
├── inventory/
│   └── hosts                # Список серверов
├── group_vars/
│   ├── all.yml              # Общие переменные
│   ├── production.yml       # Переменные для продакшена
│   └── staging.yml          # Переменные для staging
└── roles/
    ├── python/              # Роль для Python
    ├── postgresql/          # Роль для PostgreSQL
    ├── nginx/               # Роль для Nginx
    ├── django_app/          # Роль для Django приложения
    ├── redis/               # Роль для Redis
    ├── supervisor/          # Роль для Supervisor
    ├── ssl/                 # Роль для SSL
    ├── monitoring/          # Роль для мониторинга
    └── backup/              # Роль для бэкапов
```

## 🚀 Быстрый старт

### 1. Установка Ansible

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ansible

# macOS
brew install ansible

# pip
pip install ansible
```

### 2. Настройка серверов

Отредактируйте `inventory/hosts`:

```ini
[production]
your-server-1 ansible_host=1.2.3.4 ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/your-key.pem

[staging]
staging-server ansible_host=5.6.7.8 ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/staging-key.pem
```

### 3. Настройка переменных

Отредактируйте переменные в `group_vars/`:

```yaml
# group_vars/all.yml
app_name: django_backend
app_repo: "https://github.com/your-username/base-python-back.git"
django_allowed_hosts:
  - "yourdomain.com"
  - "api.yourdomain.com"
```

### 4. Настройка секретов

```bash
# Создать файл с секретами
ansible-vault create vault.yml

# Редактировать секреты
ansible-vault edit vault.yml

# Пароль для vault: your-vault-password
```

### 5. Деплой

```bash
# Проверка конфигурации
./deploy.sh production --check

# Деплой на staging
./deploy.sh staging

# Деплой на production
./deploy.sh production
```

## 🔧 Команды

### Основные команды

```bash
# Проверка подключения
ansible production -m ping

# Проверка синтаксиса
ansible-playbook --syntax-check deploy.yml

# Тестовый запуск (без изменений)
./deploy.sh production --check

# Деплой с подробным выводом
./deploy.sh production --verbose

# Деплой только определенных ролей
./deploy.sh production --tags "nginx,django_app"
```

### Управление секретами

```bash
# Создать новый vault
ansible-vault create vault.yml

# Редактировать vault
ansible-vault edit vault.yml

# Расшифровать vault (для просмотра)
ansible-vault decrypt vault.yml

# Зашифровать vault
ansible-vault encrypt vault.yml

# Изменить пароль vault
ansible-vault rekey vault.yml
```

### Управление сервисами

```bash
# Перезапуск Django
ansible production -m systemd -a "name=django state=restarted"

# Проверка статуса сервисов
ansible production -m systemd -a "name=django state=started"

# Просмотр логов
ansible production -m shell -a "journalctl -u django -f"
```

## 📋 Роли

### Python роль
- Устанавливает Python 3.11
- Создает виртуальное окружение
- Устанавливает зависимости

### PostgreSQL роль
- Устанавливает PostgreSQL
- Создает базу данных и пользователя
- Настраивает конфигурацию

### Nginx роль
- Устанавливает и настраивает Nginx
- Настраивает SSL (если включен)
- Настраивает rate limiting
- Настраивает статические файлы

### Django App роль
- Клонирует репозиторий
- Создает .env файл
- Выполняет миграции
- Собирает статические файлы
- Создает systemd сервис

### Redis роль
- Устанавливает Redis
- Настраивает конфигурацию

### SSL роль
- Настраивает SSL сертификаты
- Настраивает Let's Encrypt (если нужно)

### Monitoring роль
- Устанавливает мониторинг
- Настраивает логирование

### Backup роль
- Настраивает автоматические бэкапы
- Настраивает ротацию бэкапов

## 🔒 Безопасность

### Настройка SSH ключей

```bash
# Генерация SSH ключа
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"

# Копирование ключа на сервер
ssh-copy-id -i ~/.ssh/id_rsa.pub ubuntu@your-server-ip
```

### Настройка файрвола

```bash
# Установка UFW
ansible production -m apt -a "name=ufw state=present"

# Настройка правил
ansible production -m ufw -a "rule=allow port=22"
ansible production -m ufw -a "rule=allow port=80"
ansible production -m ufw -a "rule=allow port=443"
ansible production -m ufw -a "state=enabled"
```

## 📊 Мониторинг

### Health Check

```bash
# Проверка здоровья приложения
curl http://your-server-ip/health/

# Проверка через Ansible
ansible production -m uri -a "url=http://localhost/health/ return_content=yes"
```

### Логи

```bash
# Логи Django
journalctl -u django -f

# Логи Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Логи PostgreSQL
tail -f /var/log/postgresql/postgresql-*.log
```

## 🔄 Обновление

### Обновление кода

```bash
# Обновление только кода
./deploy.sh production --tags "django_app"

# Полное обновление
./deploy.sh production
```

### Откат

```bash
# Откат к предыдущей версии
ansible production -m git -a "repo={{ app_repo }} dest={{ app_home }}/app version=previous-commit"
ansible production -m systemd -a "name=django state=restarted"
```

## 🐛 Отладка

### Проверка конфигурации

```bash
# Проверка синтаксиса
ansible-playbook --syntax-check deploy.yml

# Проверка переменных
ansible production -m debug -a "var=hostvars[inventory_hostname]"
```

### Проблемы с подключением

```bash
# Проверка SSH
ssh -i ~/.ssh/your-key.pem ubuntu@your-server-ip

# Проверка Ansible
ansible production -m ping -vvv
```

## 📝 Переменные

### Основные переменные

```yaml
# group_vars/all.yml
app_name: django_backend
app_user: django
app_home: /opt/django_backend
app_repo: "https://github.com/your-username/base-python-back.git"
app_branch: main

python_version: "3.11"
django_debug: false
django_secret_key: "{{ vault_django_secret_key }}"

db_engine: postgresql
db_name: django_backend
db_user: django_backend_user
db_password: "{{ vault_db_password }}"

nginx_worker_processes: auto
nginx_worker_connections: 1024
```

### Переменные окружения

```yaml
# production.yml
django_allowed_hosts:
  - "yourdomain.com"
  - "api.yourdomain.com"

ssl_enabled: true
ssl_cert_path: /etc/letsencrypt/live/yourdomain.com/fullchain.pem
ssl_key_path: /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

## 🆘 Поддержка

При возникновении проблем:

1. Проверьте логи: `journalctl -u django -f`
2. Проверьте конфигурацию: `ansible-playbook --syntax-check deploy.yml`
3. Проверьте подключение: `ansible production -m ping`
4. Проверьте переменные: `ansible production -m debug -a "var=hostvars[inventory_hostname]"`

## 📚 Дополнительные ресурсы

- [Ansible Documentation](https://docs.ansible.com/)
- [Django Deployment](https://docs.djangoproject.com/en/stable/howto/deployment/)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [PostgreSQL Administration](https://www.postgresql.org/docs/)
