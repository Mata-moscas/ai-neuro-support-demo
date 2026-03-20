"""Клиент Yandex GPT через OpenAI-совместимое API."""

import logging

from openai import OpenAI

from agent.config import (
    YANDEX_GPT_API_KEY,
    YANDEX_GPT_BASE_URL,
    YANDEX_GPT_FOLDER_ID,
    YANDEX_GPT_MAX_TOKENS,
    YANDEX_GPT_MODEL,
    YANDEX_GPT_TEMPERATURE,
)

logger = logging.getLogger(__name__)


def get_llm_client() -> OpenAI:
    return OpenAI(
        base_url=YANDEX_GPT_BASE_URL,
        api_key=YANDEX_GPT_API_KEY,
        default_headers={"x-folder-id": YANDEX_GPT_FOLDER_ID} if YANDEX_GPT_FOLDER_ID else {},
    )


def chat_completion(
    client: OpenAI,
    messages: list[dict],
    tools: list[dict] | None = None,
) -> dict:
    """Вызвать Yandex GPT и вернуть ответ.

    Args:
        client: OpenAI-клиент.
        messages: История сообщений.
        tools: Описания инструментов в формате OpenAI function calling.

    Returns:
        Объект ответа (choice message).
    """
    # Убираем внутренние метаданные (_mcp_server) из инструментов
    clean_tools = None
    if tools:
        clean_tools = []
        for tool in tools:
            clean_tools.append({
                "type": tool["type"],
                "function": tool["function"],
            })

    kwargs = {
        "model": YANDEX_GPT_MODEL,
        "messages": messages,
        "temperature": YANDEX_GPT_TEMPERATURE,
        "max_tokens": YANDEX_GPT_MAX_TOKENS,
    }
    if clean_tools:
        kwargs["tools"] = clean_tools

    logger.info(f"Calling LLM with {len(messages)} messages, {len(clean_tools or [])} tools")
    response = client.chat.completions.create(**kwargs)

    return response.choices[0].message
