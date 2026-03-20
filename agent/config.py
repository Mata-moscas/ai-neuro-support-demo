"""Конфигурация агента поддержки."""

import os


# --- Yandex GPT (OpenAI-compatible API) ---
YANDEX_GPT_BASE_URL = os.getenv("YANDEX_GPT_BASE_URL", "https://llm.api.cloud.yandex.net/v1")
YANDEX_GPT_API_KEY = os.getenv("YANDEX_GPT_API_KEY", "")
YANDEX_GPT_FOLDER_ID = os.getenv("YANDEX_GPT_FOLDER_ID", "")
YANDEX_GPT_MODEL = os.getenv("YANDEX_GPT_MODEL", "yandexgpt")
YANDEX_GPT_TEMPERATURE = float(os.getenv("YANDEX_GPT_TEMPERATURE", "0.3"))
YANDEX_GPT_MAX_TOKENS = int(os.getenv("YANDEX_GPT_MAX_TOKENS", "2048"))

# --- Vector Store ---
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")
SCENARIO_TOP_K = int(os.getenv("SCENARIO_TOP_K", "3"))

# --- MCP Servers ---
MCP_SERVERS = {
    "customer_meta": os.getenv("MCP_CUSTOMER_META_URL", "http://localhost:8001/mcp"),
    "billing": os.getenv("MCP_BILLING_URL", "http://localhost:8002/mcp"),
    "incidents": os.getenv("MCP_INCIDENTS_URL", "http://localhost:8003/mcp"),
    "subscriptions": os.getenv("MCP_SUBSCRIPTIONS_URL", "http://localhost:8004/mcp"),
}

# --- Agent ---
MAX_TOOL_CALL_ROUNDS = int(os.getenv("MAX_TOOL_CALL_ROUNDS", "5"))
