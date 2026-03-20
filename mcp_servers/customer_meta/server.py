#!/usr/bin/env python3
"""MCP-сервер: базовая мета клиента (тариф, ФИО, параметры договора)."""

import os
import sys
from typing import Any

from fastmcp import FastMCP

from data import CUSTOMERS


def make_mcp() -> FastMCP:
    mcp = FastMCP(
        name="MCP-сервер метаданных клиента",
        version="1.0.0",
    )

    @mcp.tool()
    def get_customer_info(phone_number: str) -> dict[str, Any]:
        """Получить базовую информацию о клиенте по номеру телефона.

        Возвращает: тариф, ФИО, период тарификации, базовую стоимость,
        дату следующего списания, подключённые пакеты.

        Args:
            phone_number: Номер телефона клиента (например, 79001234567)

        Returns:
            Данные о клиенте в формате JSON
        """
        customer = CUSTOMERS.get(phone_number)
        if customer is None:
            return {"error": f"Клиент с номером {phone_number} не найден"}
        return customer

    return mcp


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "streamable-http")
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8001"))

    print(f"Starting Customer Meta MCP Server on {host}:{port}")
    mcp = make_mcp()
    mcp.run(transport=transport, host=host, port=port)
