#!/usr/bin/env python3
"""MCP-сервер: инциденты на сети (аварии, плановые работы)."""

import os
from typing import Any

from fastmcp import FastMCP

from data import INCIDENTS


def make_mcp() -> FastMCP:
    mcp = FastMCP(
        name="MCP-сервер инцидентов",
        version="1.0.0",
    )

    @mcp.tool()
    def get_incidents(phone_number: str) -> dict[str, Any]:
        """Получить информацию об инцидентах на сети для абонента.

        Проверяет наличие аварий, плановых работ и других проблем на сети
        в зоне обслуживания абонента. Используй этот инструмент, когда
        клиент жалуется на проблемы со связью, интернетом или качеством сервиса.

        Args:
            phone_number: Номер телефона клиента (например, 79001234567)

        Returns:
            Список инцидентов с типом, причиной и влиянием на сервис
        """
        data = INCIDENTS.get(phone_number)
        if data is None:
            return {"error": f"Данные для номера {phone_number} не найдены"}
        return data

    return mcp


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "streamable-http")
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8003"))

    print(f"Starting Incidents MCP Server on {host}:{port}")
    mcp = make_mcp()
    mcp.run(transport=transport, host=host, port=port)
