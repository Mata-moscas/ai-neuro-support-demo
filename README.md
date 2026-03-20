# AI Neuro Support Demo

Прототип агента-ассистента для поддержки клиентов телеком-оператора.
Агент автоматически классифицирует обращение, находит нужный сценарий в базе знаний,
собирает данные о клиенте и формирует ответ.

**Платформа**: Yandex AI Studio | **LLM**: YandexGPT (Responses API) | **Поиск**: Vector Store (file_search)

---

## Архитектура

```
                         ┌──────────────────────────────────────┐
                         │          Yandex AI Studio            │
                         │                                      │
                         │  ┌──────────────┐  ┌──────────────┐  │
                         │  │  YandexGPT   │  │ Vector Store │  │
                         │  │ (Responses   │  │ (file_search)│  │
                         │  │    API)      │  │ 114 сценариев│  │
                         │  └──────┬───────┘  └──────┬───────┘  │
                         │         │                  │          │
                         │         │  tool calling    │          │
                         │         │  ◄───────────────┘          │
                         └─────────┼─────────────────────────────┘
                                   │
                                   │ OpenAI-compatible API
                                   │ (Responses API)
                                   │
┌────────────┐            ┌────────┴────────┐
│            │  POST /ask │                 │
│  Оператор  ├───────────►│  FastAPI Agent  │
│  поддержки │◄───────────┤  (Python)       │
│            │   ответ    │                 │
│  Web UI    │            │  ┌────────────┐ │
│  (чат-бот) │            │  │ Tool       │ │
│            │            │  │ Executor   │ │
└────────────┘            │  │            │ │
                          │  │ get_customer│ │──► MCP Server: customer_meta
                          │  │ get_balance │ │──► MCP Server: billing
                          │  │ get_txns   │ │──► MCP Server: incidents
                          │  │ get_incid. │ │──► MCP Server: subscriptions
                          │  │ get_subs   │ │
                          │  └────────────┘ │
                          └─────────────────┘
                                   │
                           Yandex Serverless
                             Containers
```

### Цикл обработки запроса

```
Оператор                    FastAPI                 Yandex AI Studio
   │                           │                          │
   │  POST /api/ask            │                          │
   │  {question, phone}        │                          │
   │──────────────────────────►│                          │
   │                           │  responses.create()      │
   │                           │  + file_search tool      │
   │                           │  + function tools        │
   │                           │─────────────────────────►│
   │                           │                          │
   │                           │  file_search_call        │
   │                           │  (найдены сценарии)      │
   │                           │◄─────────────────────────│
   │                           │                          │
   │                           │  function_call           │
   │                           │  (get_balance, ...)      │
   │                           │◄─────────────────────────│
   │                           │                          │
   │                           │  execute function        │
   │                           │  (мок-данные / MCP)      │
   │                           │                          │
   │                           │  function_call_output    │
   │                           │─────────────────────────►│
   │                           │                          │
   │                           │  message (финальный      │
   │                           │  ответ агента)           │
   │                           │◄─────────────────────────│
   │                           │                          │
   │  {steps, answer}          │                          │
   │◄──────────────────────────│                          │
```

### Компоненты

| Компонент | Технология | Описание |
|-----------|-----------|----------|
| LLM | YandexGPT via Responses API | Генерация ответов, tool calling |
| Поиск сценариев | Vector Store (file_search) | 114 сценариев из Instructions.json |
| Функции агента | Function calling | 5 инструментов для сбора данных клиента |
| API | FastAPI | REST API + раздача Web UI |
| Web UI | Vanilla HTML/CSS/JS | Чат с отображением промежуточных шагов |
| MCP-серверы | FastMCP (опционально) | Эмуляция внутренних систем |
| Деплой | Yandex Serverless Containers | Контейнер с агентом |

---

## Структура проекта

```
ai-neuro-support-demo/
├── agent/                               # Ядро агента
│   ├── main.py                          # Оркестрация: Responses API + tool calling loop
│   ├── config.py                        # Конфигурация (API ключи, model URI, ...)
│   ├── tools.py                         # Определения функций + мок-данные
│   └── prompts/
│       └── system.txt                   # Системный промпт агента
│
├── api/                                 # REST API
│   ├── app.py                           # FastAPI: /api/ask, /api/continue, /health
│   └── schemas.py                       # Pydantic-схемы
│
├── web/
│   └── index.html                       # Веб-интерфейс чат-бота
│
├── setup/
│   └── upload_scenarios.py              # Загрузка сценариев в Yandex Vector Store
│
├── mcp_servers/                         # MCP-серверы (опционально)
│   ├── customer_meta/                   # get_customer_info
│   ├── billing/                         # get_balance, get_transactions
│   ├── incidents/                       # get_incidents
│   └── subscriptions/                   # get_subscriptions
│
├── materials/                           # Исходные материалы
│   ├── Instructions.json                # 114 сценариев поддержки
│   ├── Описание сценария.docx
│   └── ...
│
├── Dockerfile                           # Контейнер для Serverless Containers
├── docker-compose.yml                   # Локальный запуск
├── requirements.txt
├── .env.example
└── PLAN.md
```

---

## Быстрый старт

### Предварительные требования

- Python 3.10+
- Аккаунт в [Yandex Cloud](https://yandex.cloud/) с доступом к AI Studio
- Сервисный аккаунт с ролями `ai.assistants.editor` и `ai.languageModels.user`
- API-ключ с областью действия `yc.ai.foundationModels.execute`

### Шаг 1. Настройка окружения

```bash
# Клонирование репозитория
git clone <url> && cd ai-neuro-support-demo

# Виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate

# Зависимости
pip install -r requirements.txt

# Конфигурация
cp .env.example .env
```

Заполните `.env`:
```bash
YC_API_KEY=<ваш_API_ключ>
YC_FOLDER_ID=<id_каталога_в_Yandex_Cloud>
YC_MODEL=yandexgpt
```

### Шаг 2. Создание Vector Store (поискового индекса)

Загрузите 114 сценариев из `Instructions.json` в Yandex AI Studio:

```bash
python -m setup.upload_scenarios
```

Скрипт:
1. Разбивает `Instructions.json` на отдельные файлы по сценариям
2. Загружает каждый файл через Files API
3. Создаёт Vector Store (поисковый индекс)
4. Выводит `VECTOR_STORE_ID`

Добавьте полученный ID в `.env`:
```bash
VECTOR_STORE_ID=<id_из_вывода_скрипта>
```

### Шаг 3. Запуск

#### Вариант A: Локально

```bash
uvicorn api.app:app --host 0.0.0.0 --port 8080
```

Откройте http://localhost:8080 — веб-интерфейс чат-бота.

#### Вариант B: Docker

```bash
docker build -t neuro-support .
docker run -p 8080:8080 --env-file .env neuro-support
```

#### Вариант C: Docker Compose

```bash
docker compose up --build
```

---

## Деплой в Yandex Serverless Containers

### Шаг 1. Соберите и загрузите образ

```bash
# Авторизация в Container Registry
yc container registry configure-docker

# Сборка
docker build -t cr.yandex/<registry_id>/neuro-support:latest .

# Пуш
docker push cr.yandex/<registry_id>/neuro-support:latest
```

### Шаг 2. Создайте Serverless Container

```bash
yc serverless container create --name neuro-support

yc serverless container revision deploy \
  --container-name neuro-support \
  --image cr.yandex/<registry_id>/neuro-support:latest \
  --service-account-id <sa_id> \
  --execution-timeout 60s \
  --memory 512m \
  --cores 1 \
  --environment YC_API_KEY=<key>,YC_FOLDER_ID=<folder>,VECTOR_STORE_ID=<vs_id>,YC_MODEL=yandexgpt
```

### Шаг 3. Сделайте контейнер публичным (опционально)

```bash
yc serverless container allow-unauthenticated-invoke --name neuro-support
```

Контейнер будет доступен по URL вида:
`https://<container_id>.containers.yandexcloud.net`

---

## API

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/` | Веб-интерфейс чат-бота |
| GET | `/health` | Статус сервиса |
| POST | `/api/ask` | Новый вопрос → ответ агента со всеми шагами |
| POST | `/api/continue` | Продолжение диалога |

### POST /api/ask

**Запрос:**
```json
{
  "question": "У меня не работает интернет",
  "phone_number": "79001234567",
  "response_format": "text"
}
```

**Ответ:**
```json
{
  "steps": [
    {
      "type": "file_search",
      "queries": ["не работает интернет"],
      "results": [
        {"filename": "scenario_CDDA373E.txt", "score": 0.85, "text": "..."}
      ]
    },
    {
      "type": "function_call",
      "name": "get_incidents",
      "arguments": "{\"phone_number\": \"79001234567\"}"
    },
    {
      "type": "function_result",
      "name": "get_incidents",
      "result": {"network_issues": [{"type": "Плановые работы", ...}]}
    }
  ],
  "answer": "Сценарий: Проблемы с интернетом\n\nУ клиента обнаружены плановые работы...",
  "response_id": "abc-123"
}
```

### POST /api/continue

**Запрос:**
```json
{
  "message": "А какой у клиента тариф?",
  "conversation_id": "abc-123"
}
```

---

## Инструменты агента

| Функция | Описание |
|---------|----------|
| `file_search` | Поиск сценария в Vector Store (114 сценариев) |
| `get_customer_info` | Тариф, ФИО, параметры договора |
| `get_balance` | Баланс, статус, блокировки, кредитный лимит |
| `get_transactions` | Списания и платежи за 30 дней |
| `get_incidents` | Аварии и плановые работы на сети |
| `get_subscriptions` | Активные подписки клиента |

---

## Веб-интерфейс

Чат-бот доступен по адресу `/` (корень). Возможности:

- Ввод вопроса от имени клиента
- Выбор номера телефона клиента
- Выбор формата ответа (текст / JSON)
- Отображение всех промежуточных шагов:
  - 🔍 Поиск по базе знаний (file_search)
  - ⚙️ Вызовы функций (function_call)
  - ✅ Результаты функций (function_result)
- Продолжение диалога (уточняющие вопросы)

---

## Тестовые данные

Для демонстрации доступны 3 тестовых клиента:

| Телефон | ФИО | Тариф | Баланс | Особенности |
|---------|-----|-------|--------|-------------|
| 79001234567 | Иванов И.И. | Smart для своих | 83.83 ₽ | Плановые работы на сети |
| 79009876543 | Петрова М.С. | Тарифище | 1250.50 ₽ | 2 подписки (Premium + KION) |
| 79005551234 | Сидоров А.П. | НЕТАРИФ Junior | -15.20 ₽ | Блокировка, авария на сети |

---

## Переменные окружения

| Переменная | Обязательная | Описание |
|-----------|:---:|----------|
| `YC_API_KEY` | да | API-ключ Yandex Cloud |
| `YC_FOLDER_ID` | да | ID каталога в Yandex Cloud |
| `YC_MODEL` | нет | Модель (по умолчанию `yandexgpt`) |
| `YC_BASE_URL` | нет | Base URL API (по умолчанию `https://ai.api.cloud.yandex.net/v1`) |
| `VECTOR_STORE_ID` | нет | ID поискового индекса (Vector Store) |
| `MAX_TOOL_ROUNDS` | нет | Макс. раундов tool calling (по умолчанию 5) |
| `PORT` | нет | Порт сервера (по умолчанию 8080) |
