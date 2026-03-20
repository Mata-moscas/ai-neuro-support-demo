# План действий по реализации прототипа

## Этап 0. Подготовка
- [x] Организовать материалы в `materials/`
- [x] Описать архитектуру и структуру проекта в `README.md`
- [x] Составить план действий

## Этап 1. Vector Store со сценариями (Yandex AI Studio)
- [x] Скрипт загрузки `setup/upload_scenarios.py`: разбивает Instructions.json → файлы → Files API → Vector Store
- [x] Интеграция через `file_search` tool в Responses API

## Этап 2. Функции агента (эмуляция внутренних систем)
- [x] `agent/tools.py`: определения 5 функций + мок-данные из Описание сценария.docx
- [x] MCP-серверы в `mcp_servers/` для standalone-деплоя (опционально)

## Этап 3. Основной агент (Yandex AI Studio Responses API)
- [x] `agent/main.py`: цикл Responses API → file_search + function calling → execute → ответ
- [x] `agent/config.py`: конфигурация через env-переменные
- [x] `agent/prompts/system.txt`: системный промпт

## Этап 4. API + Web UI
- [x] FastAPI с эндпоинтами `/api/ask`, `/api/continue`, `/health`
- [x] Веб-интерфейс чат-бота с отображением промежуточных шагов
- [x] Dockerfile для Yandex Serverless Containers
- [x] Docker Compose для локального запуска
