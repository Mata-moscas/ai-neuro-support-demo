#!/usr/bin/env python3
"""MCP-сервер: подписки клиента (контентные и сервисные)."""

import os
from typing import Any

from fastmcp import FastMCP

from data import SUBSCRIPTIONS


def make_mcp() -> FastMCP:
    mcp = FastMCP(
        name="MCP-сервер подписок",
        version="1.0.0",
    )

    @mcp.tool()
    def get_subscriptions(phone_number: str) -> dict[str, Any]:
        """Получить список активных подписок клиента.

        Возвращает информацию обо всех подписках: название, тип (контентная/сервисная),
        стоимость, период списания, дату активации и статус.

        Args:
            phone_number: Номер телефона клиента (например, 79001234567)

        Returns:
            Список подписок клиента в формате JSON
        """
        data = SUBSCRIPTIONS.get(phone_number)
        if data is None:
            return {"error": f"Данные для номера {phone_number} не найдены"}
        return data

    return mcp


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "streamable-http")
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8004"))

    print(f"Starting Subscriptions MCP Server on {host}:{port}")
    mcp = make_mcp()
    mcp.run(transport=transport, host=host, port=port)
