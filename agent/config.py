"""Конфигурация агента поддержки — Yandex AI Studio."""

import os


# --- Yandex AI Studio ---
YC_API_KEY = os.getenv("YC_API_KEY", "")
YC_FOLDER_ID = os.getenv("YC_FOLDER_ID", "")
YC_MODEL = os.getenv("YC_MODEL", "yandexgpt")
YC_BASE_URL = os.getenv("YC_BASE_URL", "https://ai.api.cloud.yandex.net/v1")

# URI модели для Responses API
MODEL_URI = f"gpt://{YC_FOLDER_ID}/{YC_MODEL}"

# --- Vector Store (Yandex AI Studio) ---
VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID", "")

# --- Agent ---
MAX_TOOL_ROUNDS = int(os.getenv("MAX_TOOL_ROUNDS", "5"))

# --- Server ---
PORT = int(os.getenv("PORT", "8080"))
