-- Включаем расширение pg_cron
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Даём необходимые права (опционально)
GRANT USAGE ON SCHEMA cron TO doguser;