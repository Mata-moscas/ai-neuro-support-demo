"""Основной агент поддержки: оркестрация Vector Store, LLM и MCP."""

import json
import logging
import os
from dataclasses import dataclass, field

from agent.config import MAX_TOOL_CALL_ROUNDS, SCENARIO_TOP_K
from agent.llm_client import chat_completion, get_llm_client
from agent.mcp_client import call_tool, discover_tools
from vector_store.searcher import ScenarioSearcher

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompts", "system.txt")


def _load_system_prompt() -> str:
    with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


@dataclass
class Conversation:
    """Состояние диалога с агентом."""
    phone_number: str
    messages: list[dict] = field(default_factory=list)


class SupportAgent:
    """Агент поддержки клиентов.

    Принимает вопрос, ищет сценарий в Vector Store, собирает данные
    через MCP-серверы и формирует ответ с помощью Yandex GPT.
    """

    def __init__(self):
        self._llm = get_llm_client()
        self._searcher = ScenarioSearcher()
        self._tools: list[dict] = []
        self._system_prompt = _load_system_prompt()

    async def initialize(self):
        """Подключиться к MCP-серверам и получить список инструментов."""
        self._tools = await discover_tools()
        logger.info(f"Agent initialized with {len(self._tools)} tools")

    async def ask(
        self,
        question: str,
        phone_number: str,
        conversation: Conversation | None = None,
        response_format: str = "text",
    ) -> tuple[dict, Conversation]:
        """Обработать вопрос клиента.

        Args:
            question: Текст вопроса клиента.
            phone_number: Номер телефона клиента.
            conversation: Существующий диалог (для продолжения).
            response_format: "text" или "json".

        Returns:
            {"answer": str, "scenario": str | None, "format": str, "conversation_id": ...}
        """
        # 1. Поиск релевантных сценариев
        scenarios = self._searcher.search(question, top_k=SCENARIO_TOP_K)
        scenarios_text = self._format_scenarios(scenarios)

        # 2. Формирование сообщений
        if conversation is None:
            conversation = Conversation(phone_number=phone_number)
            conversation.messages = [
                {"role": "system", "content": self._system_prompt},
            ]

        format_instruction = ""
        if response_format == "json":
            format_instruction = (
                "\n\nВажно: верни ответ строго в формате JSON с полями: "
                '"scenario" (название сценария), "confidence" (уверенность 0-1), '
                '"answer" (текст ответа клиенту), "data_used" (список использованных данных), '
                '"follow_up_questions" (список уточняющих вопросов, если есть).'
            )

        user_message = (
            f"Номер телефона клиента: {phone_number}\n\n"
            f"Вопрос клиента: {question}\n\n"
            f"Найденные сценарии из базы знаний:\n{scenarios_text}"
            f"{format_instruction}"
        )
        conversation.messages.append({"role": "user", "content": user_message})

        # 3. Цикл вызовов LLM с инструментами
        answer = await self._run_tool_loop(conversation)

        detected_scenario = None
        if scenarios:
            detected_scenario = scenarios[0]["title"]

        return {
            "answer": answer,
            "scenario": detected_scenario,
            "format": response_format,
            "phone_number": phone_number,
        }, conversation

    async def continue_conversation(
        self,
        message: str,
        conversation: Conversation,
    ) -> dict:
        """Продолжить диалог (уточняющие вопросы оператора → агент).

        Args:
            message: Сообщение от оператора поддержки.
            conversation: Существующий диалог.

        Returns:
            {"answer": str, ...}
        """
        conversation.messages.append({"role": "user", "content": message})
        answer = await self._run_tool_loop(conversation)

        return {
            "answer": answer,
            "phone_number": conversation.phone_number,
        }

    async def _run_tool_loop(self, conversation: Conversation) -> str:
        """Цикл вызовов LLM → tool calls → LLM → ... → финальный ответ."""
        for round_num in range(MAX_TOOL_CALL_ROUNDS):
            response_msg = chat_completion(
                self._llm,
                conversation.messages,
                tools=self._tools if self._tools else None,
            )

            # Если нет tool_calls — возвращаем текстовый ответ
            if not response_msg.tool_calls:
                answer = response_msg.content or ""
                conversation.messages.append({"role": "assistant", "content": answer})
                return answer

            # Обрабатываем tool calls
            conversation.messages.append({
                "role": "assistant",
                "content": response_msg.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in response_msg.tool_calls
                ],
            })

            for tc in response_msg.tool_calls:
                tool_name = tc.function.name
                try:
                    arguments = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}

                logger.info(f"Round {round_num + 1}: calling tool '{tool_name}' with {arguments}")
                result = await call_tool(tool_name, arguments, self._tools)

                conversation.messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result, ensure_ascii=False),
                })

        # Если лимит раундов исчерпан
        return "Не удалось сформировать ответ: превышено максимальное количество итераций."

    @staticmethod
    def _format_scenarios(scenarios: list[dict]) -> str:
        if not scenarios:
            return "Подходящих сценариев не найдено."

        parts = []
        for i, s in enumerate(scenarios, 1):
            parts.append(
                f"### Сценарий {i}: {s['title']}\n"
                f"Код: {s['code']}\n"
                f"Релевантность (distance): {s['distance']:.4f}\n"
                f"Содержание:\n{s['content'][:2000]}\n"
            )
        return "\n".join(parts)
