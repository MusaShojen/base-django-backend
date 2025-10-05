#!/bin/bash

# Скрипт для деплоя Django Backend с помощью Ansible

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Проверка аргументов
if [ $# -eq 0 ]; then
    echo "Использование: $0 <environment> [options]"
    echo "Environments: production, staging"
    echo "Options:"
    echo "  --check     - Проверить конфигурацию без выполнения"
    echo "  --diff      - Показать изменения"
    echo "  --verbose   - Подробный вывод"
    echo "  --tags     - Выполнить только определенные теги"
    exit 1
fi

ENVIRONMENT=$1
shift

# Параметры по умолчанию
ANSIBLE_OPTS=""
CHECK_MODE=""
DIFF_MODE=""
VERBOSE=""
TAGS=""

# Обработка аргументов
while [[ $# -gt 0 ]]; do
    case $1 in
        --check)
            CHECK_MODE="--check"
            shift
            ;;
        --diff)
            DIFF_MODE="--diff"
            shift
            ;;
        --verbose)
            VERBOSE="-v"
            shift
            ;;
        --tags)
            TAGS="--tags $2"
            shift 2
            ;;
        *)
            error "Неизвестный параметр: $1"
            ;;
    esac
done

# Проверка существования inventory
if [ ! -f "inventory/hosts" ]; then
    error "Файл inventory/hosts не найден!"
fi

# Проверка существования playbook
if [ ! -f "deploy.yml" ]; then
    error "Файл deploy.yml не найден!"
fi

# Проверка подключения к серверам
log "Проверка подключения к серверам..."
ansible $ENVIRONMENT -m ping $ANSIBLE_OPTS $VERBOSE || error "Не удается подключиться к серверам!"

# Проверка синтаксиса playbook
log "Проверка синтаксиса playbook..."
ansible-playbook --syntax-check deploy.yml -i inventory/hosts $ANSIBLE_OPTS || error "Ошибка в синтаксисе playbook!"

# Выполнение деплоя
log "Начинаем деплой для окружения: $ENVIRONMENT"

if [ -n "$CHECK_MODE" ]; then
    log "Режим проверки (--check) - изменения не будут применены"
fi

if [ -n "$DIFF_MODE" ]; then
    log "Режим показа изменений (--diff)"
fi

# Команда ansible-playbook
ANSIBLE_COMMAND="ansible-playbook deploy.yml -i inventory/hosts --limit $ENVIRONMENT $ANSIBLE_OPTS $CHECK_MODE $DIFF_MODE $VERBOSE $TAGS"

log "Выполняем команду: $ANSIBLE_COMMAND"

# Выполнение команды
if $ANSIBLE_COMMAND; then
    log "Деплой успешно завершен!"
    
    if [ -z "$CHECK_MODE" ]; then
        log "Проверка статуса сервисов..."
        ansible $ENVIRONMENT -m systemd -a "name=django state=started" $ANSIBLE_OPTS
        ansible $ENVIRONMENT -m systemd -a "name=nginx state=started" $ANSIBLE_OPTS
        ansible $ENVIRONMENT -m systemd -a "name=postgresql state=started" $ANSIBLE_OPTS
        
        log "Проверка доступности приложения..."
        ansible $ENVIRONMENT -m uri -a "url=http://localhost/health/ return_content=yes" $ANSIBLE_OPTS || warn "Health check не прошел"
    fi
else
    error "Деплой завершился с ошибкой!"
fi

log "Готово!"
