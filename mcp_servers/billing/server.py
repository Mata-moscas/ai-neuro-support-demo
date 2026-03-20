#!/usr/bin/env python3
"""MCP-сервер: биллинг (баланс, статус, история списаний)."""

import os
from typing import Any

from fastmcp import FastMCP

from data import BALANCES, TRANSACTIONS


def make_mcp() -> FastMCP:
    mcp = FastMCP(
        name="MCP-сервер биллинга",
        version="1.0.0",
    )

    @mcp.tool()
    def get_balance(phone_number: str) -> dict[str, Any]:
        """Получить баланс и статус счёта клиента.

        Возвращает: текущий баланс, статус (активен/ограничен/заблокирован),
        наличие блокировок, кредитный лимит, доступные средства, тип биллинга.

        Args:
            phone_number: Номер телефона клиента (например, 79001234567)

        Returns:
            Данные о балансе в формате JSON
        """
        balance = BALANCES.get(phone_number)
        if balance is None:
            return {"error": f"Клиент с номером {phone_number} не найден"}
        return balance

    @mcp.tool()
    def get_transactions(phone_number: str) -> dict[str, Any]:
        """Получить историю списаний и платежей клиента за последние 30 дней.

        Возвращает: период, суммарные доходы/расходы, разбивку по категориям,
        детальный список транзакций с датами и описаниями.

        Args:
            phone_number: Номер телефона клиента (например, 79001234567)

        Returns:
            История транзакций в формате JSON
        """
        txns = TRANSACTIONS.get(phone_number)
        if txns is None:
            return {"error": f"Транзакции для номера {phone_number} не найдены"}
        return txns

    return mcp


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "streamable-http")
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8002"))

    print(f"Starting Billing MCP Server on {host}:{port}")
    mcp = make_mcp()
    mcp.run(transport=transport, host=host, port=port)
