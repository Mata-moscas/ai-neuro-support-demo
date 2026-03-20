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
    model_outputs = []

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

        # Описание входных данных для модели
        if round_num == 0:
            round_input_summary = user_input
        else:
            round_input_summary = f"Результаты {len(function_outputs)} функций из раунда {round_num}"

        response = client.responses.create(**kwargs)

        # Собираем решения модели для этого раунда
        round_decisions = []
        function_outputs = []

        for item in response.output:
            if item.type == "file_search_call":
                queries = getattr(item, "queries", [])
                results_list = []
                step = {
                    "type": "file_search",
                    "queries": queries,
                    "results": [],
                }
                for r in getattr(item, "results", []) or []:
                    result_entry = {
                        "filename": getattr(r, "filename", ""),
                        "score": getattr(r, "score", 0),
                        "text": getattr(r, "text", "")[:500],
                    }
                    step["results"].append(result_entry)
                    results_list.append(result_entry["filename"])
                steps.append(step)
                logger.info(f"  file_search: {len(step['results'])} results")

                round_decisions.append({
                    "action": "file_search",
                    "description": f"Поиск по базе знаний: {', '.join(queries)}",
                    "details": {"queries": queries, "results_count": len(step["results"]), "files": results_list},
                })

            elif item.type == "function_call":
                steps.append({
                    "type": "function_call",
                    "name": item.name,
                    "arguments": item.arguments,
                    "call_id": item.call_id,
                })
                logger.info(f"  function_call: {item.name}({item.arguments})")

                # Парсим аргументы для отображения
                try:
                    parsed_args = json.loads(item.arguments) if item.arguments else {}
                except json.JSONDecodeError:
                    parsed_args = {"raw": item.arguments}

                round_decisions.append({
                    "action": "function_call",
                    "description": f"Вызов функции: {item.name}",
                    "details": {"function": item.name, "arguments": parsed_args},
                })

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
                    round_decisions.append({
                        "action": "answer",
                        "description": "Генерация финального ответа",
                        "details": {"answer_length": len(text)},
                    })

        # Сохраняем информацию о раунде
        model_outputs.append({
            "round": round_num + 1,
            "model": MODEL_URI,
            "input_summary": round_input_summary,
            "decisions": round_decisions,
            "has_more": bool(function_outputs),
        })

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
        "model_outputs": model_outputs,
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
