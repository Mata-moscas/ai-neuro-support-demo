"""Основной агент поддержки — Yandex AI Studio Responses API."""

import json
import logging
import os

import openai

from agent.config import MAX_TOOL_ROUNDS, MODEL_URI, VECTOR_STORE_ID, YC_API_KEY, YC_BASE_URL, YC_FOLDER_ID
from agent.tools import FUNCTION_TOOLS, execute_function

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompts", "system.txt")


def _load_system_prompt() -> str:
    with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


SYSTEM_PROMPT = _load_system_prompt()


def get_client() -> openai.OpenAI:
    return openai.OpenAI(
        api_key=YC_API_KEY,
        base_url=YC_BASE_URL,
        project=YC_FOLDER_ID,
    )


def build_tools() -> list[dict]:
    """Собрать все инструменты: file_search (Vector Store) + function tools."""
    tools = list(FUNCTION_TOOLS)

    if VECTOR_STORE_ID:
        tools.append({
            "type": "file_search",
            "vector_store_ids": [VECTOR_STORE_ID],
        })

    return tools


def process_question(
    client: openai.OpenAI,
    question: str,
    phone_number: str,
    previous_response_id: str | None = None,
    response_format: str = "text",
) -> dict:
    """Обработать вопрос клиента. Возвращает все промежуточные шаги и ответ.

    Returns:
        {
            "steps": [...],
            "answer": str,
            "response_id": str,
        }
    """
    tools = build_tools()
    steps = []

    # Формируем input
    format_hint = ""
    if response_format == "json":
        format_hint = (
            "\n\nВажно: верни ответ строго в формате JSON с полями: "
            '"scenario", "confidence", "answer", "data_used", "follow_up_questions".'
        )

    user_input = (
        f"Номер телефона клиента: {phone_number}\n"
        f"Вопрос клиента: {question}"
        f"{format_hint}"
    )

    input_data: str | list = user_input

    kwargs = {
        "model": MODEL_URI,
        "instructions": SYSTEM_PROMPT,
        "tools": tools,
        "input": input_data,
    }
    if previous_response_id:
        kwargs["previous_response_id"] = previous_response_id

    # Цикл: LLM → tool calls → execute → LLM → ...
    response = None
    for round_num in range(MAX_TOOL_ROUNDS):
        logger.info(f"Round {round_num + 1}: calling Responses API")

        response = client.responses.create(**kwargs)

        # Собираем шаги из output
        function_outputs = []

        for item in response.output:
            if item.type == "file_search_call":
                step = {
                    "type": "file_search",
                    "queries": getattr(item, "queries", []),
                    "results": [],
                }
                for r in getattr(item, "results", []) or []:
                    step["results"].append({
                        "filename": getattr(r, "filename", ""),
                        "score": getattr(r, "score", 0),
                        "text": getattr(r, "text", "")[:500],
                    })
                steps.append(step)
                logger.info(f"  file_search: {len(step['results'])} results")

            elif item.type == "function_call":
                steps.append({
                    "type": "function_call",
                    "name": item.name,
                    "arguments": item.arguments,
                    "call_id": item.call_id,
                })
                logger.info(f"  function_call: {item.name}({item.arguments})")

                # Выполняем функцию
                result = execute_function(item.name, item.arguments)
                result_json = json.dumps(result, ensure_ascii=False)

                steps.append({
                    "type": "function_result",
                    "name": item.name,
                    "result": result,
                })
                logger.info(f"  function_result: {item.name} -> {result_json[:200]}")

                function_outputs.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": result_json,
                })

            elif item.type == "message":
                # Финальный текстовый ответ
                text = ""
                for content_block in getattr(item, "content", []):
                    if getattr(content_block, "type", "") == "output_text":
                        text += getattr(content_block, "text", "")
                if text:
                    steps.append({"type": "answer", "text": text})

        # Если нет function_calls — цикл завершён
        if not function_outputs:
            break

        # Продолжаем с результатами функций
        kwargs = {
            "model": MODEL_URI,
            "instructions": SYSTEM_PROMPT,
            "tools": tools,
            "input": function_outputs,
            "previous_response_id": response.id,
        }

    answer = getattr(response, "output_text", "") if response else ""

    return {
        "steps": steps,
        "answer": answer,
        "response_id": response.id if response else None,
    }


def continue_dialog(
    client: openai.OpenAI,
    message: str,
    previous_response_id: str,
) -> dict:
    """Продолжить диалог (уточняющий вопрос оператора)."""
    return process_question(
        client=client,
        question=message,
        phone_number="",  # уже известен из контекста
        previous_response_id=previous_response_id,
    )
