# AI Neuro Support Demo

Прототип агента-ассистента для поддержки клиентов телеком-оператора (МТС).
Агент автоматически классифицирует обращение, находит нужный сценарий, собирает данные о клиенте из внутренних систем и формирует ответ.

**LLM**: Yandex GPT через OpenAI-совместимое API | **MCP**: FastMCP | **Vector Store**: ChromaDB

---

## Структура проекта

```
ai-neuro-support-demo/
├── README.md
├── PLAN.md                              # План действий
├── .env.example                         # Пример переменных окружения
├── requirements.txt                     # Зависимости агента
├── Dockerfile                           # Docker-образ агента
├── docker-compose.yml                   # Оркестрация всех сервисов
│
├── agent/                               # Основной агент поддержки
│   ├── main.py                          # SupportAgent — оркестрация всего цикла
│   ├── config.py                        # Конфигурация (API ключи, URLs, параметры)
│   ├── llm_client.py                    # Клиент Yandex GPT (OpenAI SDK)
│   ├── mcp_client.py                    # MCP-клиент (подключение к серверам, вызов инструментов)
│   └── prompts/
│       └── system.txt                   # Системный промпт агента
│
├── vector_store/                        # Vector Store со сценариями
│   ├── indexer.py                       # Индексация Instructions.json → ChromaDB
│   └── searcher.py                      # Семантический поиск сценариев
│
├── mcp_servers/                         # MCP-серверы (эмуляция внутренних систем)
│   ├── customer_meta/                   # Мета клиента: тариф, ФИО, параметры договора
│   │   ├── server.py                    #   tool: get_customer_info(phone_number)
│   │   ├── data.py                      #   мок-данные
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── billing/                         # Биллинг: баланс, статус, история списаний
│   │   ├── server.py                    #   tools: get_balance, get_transactions
│   │   ├── data.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── incidents/                       # Инциденты: аварии, плановые работы
│   │   ├── server.py                    #   tool: get_incidents(phone_number)
│   │   ├── data.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── subscriptions/                   # Подписки: контентные и сервисные
│       ├── server.py                    #   tool: get_subscriptions(phone_number)
│       ├── data.py
│       ├── Dockerfile
│       └── requirements.txt
│
├── api/                                 # REST API (FastAPI)
│   ├── app.py                           # Эндпоинты: /ask, /ask/{id}, /health
│   └── schemas.py                       # Pydantic-схемы запросов/ответов
│
└── materials/                           # Справочные материалы (исходные файлы)
    ├── Instructions.json                # 114 сценариев поддержки
    ├── Описание сценария.docx           # Примеры мета-данных клиента
    ├── Инструкция по MCP.pdf
    ├── geocoder.py
    ├── instructions/
    └── weather-mcp/                     # Пример MCP-сервера (погода)
```

---

## Архитектура

```
┌─────────────────┐
│  Пользователь   │  (текст / голос → текст)
└────────┬────────┘
         │
         ▼
┌─────────────────┐     POST /ask
│   FastAPI (API)  │◄───────────────── Оператор поддержки / НейроСаппорт
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│              SupportAgent                        │
│                                                  │
│  1. Поиск сценария → Vector Store (ChromaDB)     │
│     114 сценариев из Instructions.json           │
│                                                  │
│  2. Yandex GPT (OpenAI API) ──── tool calling ──►│
│                                                  │
│  3. MCP-серверы (streamable-http)                │
│     ├── customer_meta :8001  (тариф, ФИО)       │
│     ├── billing       :8002  (баланс, списания) │
│     ├── incidents     :8003  (аварии на сети)   │
│     └── subscriptions :8004  (подписки)         │
│                                                  │
│  4. Ответ → текст / JSON                        │
└─────────────────────────────────────────────────┘
```

### Цикл обработки запроса

1. Оператор отправляет вопрос клиента + номер телефона через `POST /ask`
2. Агент ищет релевантные сценарии в Vector Store (top-3)
3. Агент отправляет вопрос + сценарии + инструменты в Yandex GPT
4. LLM решает, какие данные нужны, и вызывает MCP-инструменты (tool calling)
5. Агент исполняет вызовы через MCP-клиент → получает данные
6. LLM формирует финальный ответ на основе данных и сценария
7. Ответ возвращается оператору (текст или JSON)

---

## Быстрый старт

### 1. Настройка

```bash
cp .env.example .env
# Заполните YANDEX_GPT_API_KEY и YANDEX_GPT_FOLDER_ID
```

### 2. Запуск через Docker Compose

```bash
docker compose up --build
```

Это поднимет:
- 4 MCP-сервера (порты 8001–8004)
- Агент с API (порт 8000)

### 3. Проверка

```bash
# Здоровье
curl http://localhost:8000/health

# Вопрос
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "У меня не работает домашний интернет",
    "phone_number": "79001234567",
    "response_format": "text"
  }'
```

### 4. Локальный запуск (без Docker)

```bash
pip install -r requirements.txt

# Запуск MCP-серверов (в отдельных терминалах)
python mcp_servers/customer_meta/server.py
python mcp_servers/billing/server.py
python mcp_servers/incidents/server.py
python mcp_servers/subscriptions/server.py

# Запуск агента
uvicorn api.app:app --host 0.0.0.0 --port 8000
```

---

## API

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET   | `/health` | Статус сервиса (кол-во инструментов, сценариев) |
| POST  | `/ask` | Основной запрос: вопрос клиента → ответ агента |
| POST  | `/ask/{conversation_id}` | Продолжение диалога (уточняющие вопросы) |

### POST /ask — формат запроса

```json
{
  "question": "Почему у меня списали деньги?",
  "phone_number": "79001234567",
  "response_format": "text"
}
```

### POST /ask — формат ответа

```json
{
  "answer": "Черновик ответа для оператора...",
  "scenario": "Непоступление платежа / Проблемы при оплате",
  "format": "text",
  "phone_number": "79001234567",
  "conversation_id": "uuid-xxx"
}
```

---

## MCP-инструменты

| Инструмент | Сервер | Описание |
|-----------|--------|----------|
| `get_customer_info` | customer_meta | Тариф, ФИО, параметры договора |
| `get_balance` | billing | Баланс, статус, блокировки, кредитный лимит |
| `get_transactions` | billing | Списания и платежи за 30 дней |
| `get_incidents` | incidents | Аварии и плановые работы на сети |
| `get_subscriptions` | subscriptions | Активные подписки клиента |

---

## Технологический стек

| Компонент | Технология |
|-----------|-----------|
| LLM | Yandex GPT via OpenAI-compatible API |
| Vector Store | ChromaDB (default embedding function) |
| MCP-серверы | Python + FastMCP (streamable-http) |
| API | FastAPI + Pydantic |
| MCP-клиент | mcp Python SDK |
| Контейнеризация | Docker + Docker Compose |
| Язык | Python 3.11+ |
