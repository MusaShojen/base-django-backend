# Makefile для Ansible деплоя

.PHONY: help check deploy staging production clean vault-edit vault-view

# Цвета
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m # No Color

help: ## Показать справку
	@echo "$(GREEN)Ansible Deployment Commands$(NC)"
	@echo ""
	@echo "$(YELLOW)Основные команды:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

check: ## Проверить конфигурацию
	@echo "$(GREEN)Проверка синтаксиса playbook...$(NC)"
	ansible-playbook --syntax-check deploy.yml
	@echo "$(GREEN)Проверка подключения к серверам...$(NC)"
	ansible production -m ping
	ansible staging -m ping

deploy-staging: ## Деплой на staging
	@echo "$(GREEN)Деплой на staging...$(NC)"
	./deploy.sh staging

deploy-production: ## Деплой на production
	@echo "$(GREEN)Деплой на production...$(NC)"
	./deploy.sh production

deploy-staging-check: ## Проверка деплоя на staging
	@echo "$(GREEN)Проверка деплоя на staging...$(NC)"
	./deploy.sh staging --check

deploy-production-check: ## Проверка деплоя на production
	@echo "$(GREEN)Проверка деплоя на production...$(NC)"
	./deploy.sh production --check

vault-edit: ## Редактировать vault файл
	@echo "$(GREEN)Редактирование vault файла...$(NC)"
	ansible-vault edit vault.yml

vault-view: ## Просмотреть vault файл
	@echo "$(GREEN)Просмотр vault файла...$(NC)"
	ansible-vault view vault.yml

vault-create: ## Создать новый vault файл
	@echo "$(GREEN)Создание нового vault файла...$(NC)"
	ansible-vault create vault.yml

vault-encrypt: ## Зашифровать vault файл
	@echo "$(GREEN)Зашифровка vault файла...$(NC)"
	ansible-vault encrypt vault.yml

vault-decrypt: ## Расшифровать vault файл
	@echo "$(GREEN)Расшифровка vault файла...$(NC)"
	ansible-vault decrypt vault.yml

ping: ## Проверить подключение к серверам
	@echo "$(GREEN)Проверка подключения к production...$(NC)"
	ansible production -m ping
	@echo "$(GREEN)Проверка подключения к staging...$(NC)"
	ansible staging -m ping

status: ## Проверить статус сервисов
	@echo "$(GREEN)Статус сервисов на production...$(NC)"
	ansible production -m systemd -a "name=django state=started"
	ansible production -m systemd -a "name=nginx state=started"
	ansible production -m systemd -a "name=postgresql state=started"

logs: ## Просмотреть логи Django
	@echo "$(GREEN)Логи Django на production...$(NC)"
	ansible production -m shell -a "journalctl -u django -n 50"

restart-django: ## Перезапустить Django
	@echo "$(GREEN)Перезапуск Django на production...$(NC)"
	ansible production -m systemd -a "name=django state=restarted"

restart-nginx: ## Перезапустить Nginx
	@echo "$(GREEN)Перезапуск Nginx на production...$(NC)"
	ansible production -m systemd -a "name=nginx state=restarted"

restart-all: ## Перезапустить все сервисы
	@echo "$(GREEN)Перезапуск всех сервисов на production...$(NC)"
	ansible production -m systemd -a "name=django state=restarted"
	ansible production -m systemd -a "name=nginx state=restarted"
	ansible production -m systemd -a "name=postgresql state=restarted"

health-check: ## Проверить здоровье приложения
	@echo "$(GREEN)Проверка здоровья приложения...$(NC)"
	ansible production -m uri -a "url=http://localhost/health/ return_content=yes"

update-code: ## Обновить только код приложения
	@echo "$(GREEN)Обновление кода приложения...$(NC)"
	./deploy.sh production --tags "django_app"

update-nginx: ## Обновить только Nginx
	@echo "$(GREEN)Обновление Nginx...$(NC)"
	./deploy.sh production --tags "nginx"

update-db: ## Обновить только базу данных
	@echo "$(GREEN)Обновление базы данных...$(NC)"
	./deploy.sh production --tags "postgresql"

ssl-setup: ## Настроить SSL сертификаты
	@echo "$(GREEN)Настройка SSL сертификатов...$(NC)"
	./deploy.sh production --tags "ssl"

ssl-renew: ## Обновить SSL сертификаты
	@echo "$(GREEN)Обновление SSL сертификатов...$(NC)"
	ansible production -m shell -a "certbot renew --nginx"

ssl-test: ## Тестировать SSL сертификаты
	@echo "$(GREEN)Тестирование SSL сертификатов...$(NC)"
	ansible production -m shell -a "certbot renew --dry-run"

clean: ## Очистить временные файлы
	@echo "$(GREEN)Очистка временных файлов...$(NC)"
	find . -name "*.retry" -delete
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

install-deps: ## Установить зависимости Ansible
	@echo "$(GREEN)Установка зависимостей...$(NC)"
	pip install ansible

test-connection: ## Тестировать подключение
	@echo "$(GREEN)Тестирование подключения...$(NC)"
	ansible production -m ping -vvv
	ansible staging -m ping -vvv

show-vars: ## Показать переменные
	@echo "$(GREEN)Переменные для production...$(NC)"
	ansible production -m debug -a "var=hostvars[inventory_hostname]"

show-facts: ## Показать факты о серверах
	@echo "$(GREEN)Факты о production серверах...$(NC)"
	ansible production -m setup

# Алиасы
staging: deploy-staging
production: deploy-production
check-staging: deploy-staging-check
check-production: deploy-production-check
