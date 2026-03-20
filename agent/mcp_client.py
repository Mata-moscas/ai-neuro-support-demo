"""MCP-клиент: подключение к MCP-серверам и вызов инструментов."""

import json
import logging
from typing import Any

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from agent.config import MCP_SERVERS

logger = logging.getLogger(__name__)


async def discover_tools() -> list[dict]:
    """Опросить все MCP-серверы и получить список доступных инструментов.

    Returns:
        Список инструментов в формате OpenAI function calling.
    """
    openai_tools = []

    for server_name, server_url in MCP_SERVERS.items():
        try:
            async with streamablehttp_client(server_url) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools_result = await session.list_tools()

                    for tool in tools_result.tools:
                        openai_tools.append({
                            "type": "function",
                            "function": {
                                "name": tool.name,
                                "description": tool.description or "",
                                "parameters": tool.inputSchema,
                            },
                            "_mcp_server": server_name,
                        })
                        logger.info(f"Discovered tool '{tool.name}' from {server_name}")
        except Exception as e:
            logger.warning(f"Failed to connect to MCP server '{server_name}' at {server_url}: {e}")

    return openai_tools


async def call_tool(tool_name: str, arguments: dict[str, Any], tools: list[dict]) -> Any:
    """Вызвать инструмент на соответствующем MCP-сервере.

    Args:
        tool_name: Имя инструмента.
        arguments: Аргументы вызова.
        tools: Список инструментов (с метаданными _mcp_server).

    Returns:
        Результат вызова инструмента.
    """
    server_name = None
    for tool in tools:
        if tool["function"]["name"] == tool_name:
            server_name = tool.get("_mcp_server")
            break

    if server_name is None:
        return {"error": f"Tool '{tool_name}' not found"}

    server_url = MCP_SERVERS.get(server_name)
    if server_url is None:
        return {"error": f"Server '{server_name}' not configured"}

    try:
        async with streamablehttp_client(server_url) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=arguments)

                # Извлекаем текст из результата MCP
                if result.content:
                    for block in result.content:
                        if hasattr(block, "text"):
                            try:
                                return json.loads(block.text)
                            except json.JSONDecodeError:
                                return {"result": block.text}
                return {"result": "empty response"}
    except Exception as e:
        logger.error(f"Error calling tool '{tool_name}' on '{server_name}': {e}")
        return {"error": str(e)}
