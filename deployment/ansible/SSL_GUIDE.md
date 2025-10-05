# 🔒 SSL Certificate Management Guide

Руководство по управлению SSL сертификатами с помощью Let's Encrypt и Certbot.

## 🚀 Автоматическая настройка SSL

### 1. Включение SSL

В файле `group_vars/production.yml`:

```yaml
# SSL настройки
ssl_enabled: true
ssl_email: "admin@yourdomain.com"  # Email для Let's Encrypt
django_allowed_hosts:
  - "yourdomain.com"
  - "api.yourdomain.com"
```

### 2. Деплой с SSL

```bash
# Настройка SSL сертификатов
make ssl-setup

# Или полный деплой
make production
```

## 🔄 Автоматическое продление

### Certbot автоматически:

1. **Получает сертификаты** при первом запуске
2. **Продлевает сертификаты** каждые 3 месяца
3. **Обновляет Nginx** конфигурацию
4. **Отправляет уведомления** о проблемах

### Расписание продления:

```bash
# Проверка каждые 12 часов
0 */12 * * * certbot renew --quiet --nginx

# Основное продление в 2:00 каждый день
0 2 * * * certbot renew --quiet --nginx
```

## 📊 Мониторинг SSL

### Автоматический мониторинг:

- **Проверка каждые 6 часов** (6:00, 12:00, 18:00, 00:00)
- **Email уведомления** за 30 дней до истечения
- **Критические уведомления** за 7 дней до истечения
- **Логирование** всех проверок

### Ручная проверка:

```bash
# Проверить срок действия
make ssl-test

# Проверить статус сертификатов
ansible production -m shell -a "certbot certificates"

# Проверить логи мониторинга
ansible production -m shell -a "tail -f {{ app_home }}/logs/ssl_monitor.log"
```

## 🛠️ Управление SSL

### Основные команды:

```bash
# Настройка SSL
make ssl-setup

# Принудительное обновление
make ssl-renew

# Тестирование обновления
make ssl-test

# Проверка статуса
ansible production -m shell -a "certbot certificates"
```

### Ручные команды:

```bash
# Получить новый сертификат
certbot certonly --nginx -d yourdomain.com

# Обновить все сертификаты
certbot renew --nginx

# Тестовое обновление
certbot renew --dry-run

# Удалить сертификат
certbot delete --cert-name yourdomain.com
```

## 🔍 Диагностика проблем

### Проверка сертификатов:

```bash
# Проверить срок действия
openssl x509 -in /etc/letsencrypt/live/yourdomain.com/fullchain.pem -text -noout | grep "Not After"

# Проверить цепочку сертификатов
openssl verify -CAfile /etc/letsencrypt/live/yourdomain.com/chain.pem /etc/letsencrypt/live/yourdomain.com/cert.pem

# Проверить SSL с сайта
curl -I https://yourdomain.com
```

### Логи и отладка:

```bash
# Логи Certbot
tail -f /var/log/letsencrypt/letsencrypt.log

# Логи Nginx
tail -f /var/log/nginx/error.log

# Логи мониторинга SSL
tail -f {{ app_home }}/logs/ssl_monitor.log

# Тестирование SSL
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

## ⚙️ Конфигурация

### Nginx SSL настройки:

```nginx
# SSL Security
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;

# HSTS
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### Certbot настройки:

```bash
# Конфигурация в /etc/letsencrypt/cli.ini
email = admin@yourdomain.com
agree-tos = true
non-interactive = true
```

## 🚨 Устранение проблем

### Проблема: Сертификат не обновляется

```bash
# Проверить статус
certbot certificates

# Принудительное обновление
certbot renew --force-renewal --nginx

# Проверить логи
journalctl -u certbot.timer
```

### Проблема: Nginx не перезапускается

```bash
# Проверить конфигурацию
nginx -t

# Перезапустить Nginx
systemctl restart nginx

# Проверить статус
systemctl status nginx
```

### Проблема: Домен не резолвится

```bash
# Проверить DNS
nslookup yourdomain.com
dig yourdomain.com

# Проверить доступность
curl -I http://yourdomain.com
```

## 📧 Email уведомления

### Настройка email:

```yaml
# В group_vars/production.yml
ssl_email: "admin@yourdomain.com"
```

### Установка mail:

```bash
# Ubuntu/Debian
apt install mailutils

# Настройка
echo "root: admin@yourdomain.com" >> /etc/aliases
newaliases
```

## 🔐 Безопасность

### Рекомендации:

1. **Используйте сильные SSL настройки**
2. **Включите HSTS**
3. **Мониторьте срок действия**
4. **Регулярно обновляйте Certbot**
5. **Используйте только TLS 1.2+**

### Проверка безопасности:

```bash
# Тестирование SSL
curl -I https://yourdomain.com

# Проверка рейтинга SSL
# Используйте https://www.ssllabs.com/ssltest/
```

## 📅 Расписание задач

### Автоматические задачи:

```bash
# Продление сертификатов (каждый день в 2:00)
0 2 * * * certbot renew --quiet --nginx

# Мониторинг SSL (каждые 6 часов)
0 */6 * * * {{ app_home }}/ssl_monitor.sh

# Бэкап сертификатов (еженедельно)
0 3 * * 0 tar -czf {{ app_home }}/backups/ssl_$(date +\%Y\%m\%d).tar.gz /etc/letsencrypt/
```

## 🆘 Поддержка

### Полезные команды:

```bash
# Статус всех сертификатов
certbot certificates

# Тестирование обновления
certbot renew --dry-run

# Проверка конфигурации
nginx -t

# Перезапуск сервисов
systemctl restart nginx
systemctl restart certbot
```

### Контакты:

- **Let's Encrypt**: https://letsencrypt.org/
- **Certbot документация**: https://certbot.eff.org/
- **SSL Labs тест**: https://www.ssllabs.com/ssltest/

## 📝 Changelog

### v1.0.0
- Автоматическое получение SSL сертификатов
- Автоматическое продление каждые 3 месяца
- Мониторинг с email уведомлениями
- HSTS и безопасные SSL настройки
- Интеграция с Nginx
