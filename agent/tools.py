"""Определения инструментов (tools) и их реализации.

Инструменты вызываются агентом через Yandex AI Studio Responses API
в формате function calling. Реализации возвращают мок-данные.
"""

import json
from typing import Any

# ── Мок-данные (из Описание сценария.docx) ──────────────────────────────────

_CUSTOMERS = {
    "79001234567": {
        "phone": "79001234567",
        "data_as_of": "2026-02-13T08:27:46+00:00",
        "full_name": "Иванов Иван Иванович",
        "tariff": "Smart для своих 062016",
        "tariff_full_name": "Смоленск - Smart для своих 062016 (МАСС) (SCP)",
        "billing_period": "Месяц",
        "base_price": 310.00,
        "currency": "RUB",
        "next_charge_date": "2026-02-23T00:00:00+03:00",
        "last_charge": 310.00,
        "packages": "Нет (тариф с поминутной/помегабайтной тарификацией)",
    },
    "79009876543": {
        "phone": "79009876543",
        "data_as_of": "2026-02-13T10:15:00+00:00",
        "full_name": "Петрова Мария Сергеевна",
        "tariff": "Тарифище",
        "tariff_full_name": "Москва - Тарифище (МАСС)",
        "billing_period": "Месяц",
        "base_price": 650.00,
        "currency": "RUB",
        "next_charge_date": "2026-03-01T00:00:00+03:00",
        "last_charge": 650.00,
        "packages": "Интернет 30 ГБ, Минуты 500, SMS 50",
    },
    "79005551234": {
        "phone": "79005551234",
        "data_as_of": "2026-02-13T12:00:00+00:00",
        "full_name": "Сидоров Алексей Павлович",
        "tariff": "НЕТАРИФ Junior",
        "tariff_full_name": "Санкт-Петербург - НЕТАРИФ Junior (МАСС)",
        "billing_period": "Месяц",
        "base_price": 200.00,
        "currency": "RUB",
        "next_charge_date": "2026-02-28T00:00:00+03:00",
        "last_charge": 200.00,
        "packages": "Интернет 10 ГБ, Минуты 200",
    },
}

_BALANCES = {
    "79001234567": {
        "phone": "79001234567",
        "balance": 83.83,
        "currency": "RUB",
        "status": "Активен (все услуги активны и доступны)",
        "blockages": "Нет",
        "credit_limit": 377.00,
        "available": 460.83,
        "billing_type": "Кредитная",
    },
    "79009876543": {
        "phone": "79009876543",
        "balance": 1250.50,
        "currency": "RUB",
        "status": "Активен",
        "blockages": "Нет",
        "credit_limit": 0.00,
        "available": 1250.50,
        "billing_type": "Авансовая",
    },
    "79005551234": {
        "phone": "79005551234",
        "balance": -15.20,
        "currency": "RUB",
        "status": "Ограничен (исходящие вызовы заблокированы)",
        "blockages": "Финансовая блокировка: исходящие вызовы",
        "credit_limit": 0.00,
        "available": -15.20,
        "billing_type": "Авансовая",
    },
}

_TRANSACTIONS = {
    "79001234567": {
        "phone": "79001234567",
        "period": "30 дней",
        "total_income": 300.00,
        "total_expenses": 311.20,
        "currency": "RUB",
        "transactions": [
            {"date": "2026-01-23", "amount": -310.00, "description": "Ежемесячная плата Smart для своих"},
            {"date": "2026-01-20", "amount": 1.20, "description": "Компенсация комиссии за платёж"},
            {"date": "2026-01-20", "amount": 300.00, "description": "Регистрация платежа: СБП_Мой МТС"},
        ],
    },
    "79009876543": {
        "phone": "79009876543",
        "period": "30 дней",
        "total_income": 1000.00,
        "total_expenses": 650.00,
        "currency": "RUB",
        "transactions": [
            {"date": "2026-02-01", "amount": -650.00, "description": "Ежемесячная плата Тарифище"},
            {"date": "2026-01-25", "amount": 1000.00, "description": "Регистрация платежа: Банковская карта"},
        ],
    },
    "79005551234": {
        "phone": "79005551234",
        "period": "30 дней",
        "total_income": 0.00,
        "total_expenses": 215.20,
        "currency": "RUB",
        "transactions": [
            {"date": "2026-01-28", "amount": -200.00, "description": "Ежемесячная плата НЕТАРИФ Junior"},
            {"date": "2026-01-30", "amount": -15.20, "description": "Подписка МТС Premium (контентная)"},
        ],
    },
}

_INCIDENTS = {
    "79001234567": {
        "phone": "79001234567",
        "network_issues": [
            {
                "type": "Плановые работы",
                "number": "MSK000015767628",
                "cause": "Отключение БС по предписанию",
                "impact": "Значительное влияние на сервис абонентам в зоне действия СЭ",
                "status": "В работе",
            },
        ],
    },
    "79009876543": {"phone": "79009876543", "network_issues": []},
    "79005551234": {
        "phone": "79005551234",
        "network_issues": [
            {
                "type": "Авария",
                "number": "SPB000098712345",
                "cause": "Обрыв оптического кабеля",
                "impact": "Полная потеря связи для абонентов в зоне действия СЭ",
                "status": "В работе",
            },
        ],
    },
}

_SUBSCRIPTIONS = {
    "79001234567": {"phone": "79001234567", "subscriptions": []},
    "79009876543": {
        "phone": "79009876543",
        "subscriptions": [
            {"name": "МТС Premium", "price": 299.00, "period": "Месяц", "status": "Активна"},
            {"name": "KION", "price": 199.00, "period": "Месяц", "status": "Активна"},
        ],
    },
    "79005551234": {
        "phone": "79005551234",
        "subscriptions": [
            {"name": "МТС Premium", "price": 15.20, "period": "Ежедневно", "status": "Активна"},
        ],
    },
}


# ── Реализации функций ──────────────────────────────────────────────────────

def get_customer_info(phone_number: str) -> dict[str, Any]:
    data = _CUSTOMERS.get(phone_number)
    if data is None:
        return {"error": f"Клиент с номером {phone_number} не найден"}
    return data


def get_balance(phone_number: str) -> dict[str, Any]:
    data = _BALANCES.get(phone_number)
    if data is None:
        return {"error": f"Клиент с номером {phone_number} не найден"}
    return data


def get_transactions(phone_number: str) -> dict[str, Any]:
    data = _TRANSACTIONS.get(phone_number)
    if data is None:
        return {"error": f"Транзакции для номера {phone_number} не найдены"}
    return data


def get_incidents(phone_number: str) -> dict[str, Any]:
    data = _INCIDENTS.get(phone_number)
    if data is None:
        return {"error": f"Данные для номера {phone_number} не найдены"}
    return data


def get_subscriptions(phone_number: str) -> dict[str, Any]:
    data = _SUBSCRIPTIONS.get(phone_number)
    if data is None:
        return {"error": f"Данные для номера {phone_number} не найдены"}
    return data


# ── Маппинг имя → функция ───────────────────────────────────────────────────

FUNCTION_MAP: dict[str, callable] = {
    "get_customer_info": get_customer_info,
    "get_balance": get_balance,
    "get_transactions": get_transactions,
    "get_incidents": get_incidents,
    "get_subscriptions": get_subscriptions,
}


def execute_function(name: str, arguments_json: str) -> dict[str, Any]:
    """Выполнить функцию по имени и вернуть результат."""
    fn = FUNCTION_MAP.get(name)
    if fn is None:
        return {"error": f"Неизвестная функция: {name}"}
    try:
        args = json.loads(arguments_json) if isinstance(arguments_json, str) else arguments_json
        return fn(**args)
    except Exception as e:
        return {"error": str(e)}


# ── Определения инструментов для Responses API ──────────────────────────────

PHONE_PARAM = {
    "type": "object",
    "properties": {
        "phone_number": {
            "type": "string",
            "description": "Номер телефона клиента (например, 79001234567)",
        },
    },
    "required": ["phone_number"],
}

FUNCTION_TOOLS = [
    {
        "type": "function",
        "name": "get_customer_info",
        "description": (
            "Получить базовую информацию о клиенте: тариф, ФИО, "
            "параметры договора, дату следующего списания, подключённые пакеты."
        ),
        "parameters": PHONE_PARAM,
    },
    {
        "type": "function",
        "name": "get_balance",
        "description": (
            "Получить баланс и статус счёта клиента: текущий баланс, статус, "
            "блокировки, кредитный лимит, доступные средства, тип биллинга."
        ),
        "parameters": PHONE_PARAM,
    },
    {
        "type": "function",
        "name": "get_transactions",
        "description": (
            "Получить историю списаний и платежей за последние 30 дней: "
            "суммарные доходы/расходы, детальный список транзакций."
        ),
        "parameters": PHONE_PARAM,
    },
    {
        "type": "function",
        "name": "get_incidents",
        "description": (
            "Проверить инциденты на сети для абонента: аварии, плановые работы, "
            "влияние на сервис. Используй при жалобах на связь или интернет."
        ),
        "parameters": PHONE_PARAM,
    },
    {
        "type": "function",
        "name": "get_subscriptions",
        "description": (
            "Получить список активных подписок клиента: название, стоимость, "
            "период списания, статус."
        ),
        "parameters": PHONE_PARAM,
    },
]
