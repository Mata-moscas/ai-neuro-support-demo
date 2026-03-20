"""Мок-данные биллинга: баланс, статус, история списаний."""

BALANCES = {
    "79001234567": {
        "phone": "79001234567",
        "data_as_of": "2026-02-13T08:35:27+00:00",
        "balance": 83.83,
        "currency": "RUB",
        "status": "Активен (все услуги активны и доступны)",
        "blockages": "Нет (низкий баланс не блокирует услуги)",
        "credit_limit": 377.00,
        "available": 460.83,
        "billing_type": "Кредитная",
    },
    "79009876543": {
        "phone": "79009876543",
        "data_as_of": "2026-02-13T10:20:00+00:00",
        "balance": 1250.50,
        "currency": "RUB",
        "status": "Активен (все услуги активны и доступны)",
        "blockages": "Нет",
        "credit_limit": 0.00,
        "available": 1250.50,
        "billing_type": "Авансовая",
    },
    "79005551234": {
        "phone": "79005551234",
        "data_as_of": "2026-02-13T12:05:00+00:00",
        "balance": -15.20,
        "currency": "RUB",
        "status": "Ограничен (исходящие вызовы заблокированы)",
        "blockages": "Добровольная блокировка отсутствует. Финансовая блокировка: исходящие вызовы",
        "credit_limit": 0.00,
        "available": -15.20,
        "billing_type": "Авансовая",
    },
}

TRANSACTIONS = {
    "79001234567": {
        "phone": "79001234567",
        "period_start": "2026-01-14T08:29:02+00:00",
        "period_end": "2026-02-13T08:29:02+00:00",
        "period_days": 30,
        "total_income": 300.00,
        "total_expenses": 311.20,
        "period_balance_change": -11.20,
        "currency": "RUB",
        "income_by_category": [
            {"category": "Платёж", "amount": 300.00},
        ],
        "expenses_by_category": [
            {"category": "Абонентская плата", "amount": 310.00},
            {"category": "Дополнительные услуги", "amount": 1.20},
        ],
        "transactions": [
            {
                "date": "2026-01-23T03:31:09+03:00",
                "amount": -310.00,
                "description": "Ежемесячная плата Smart для своих",
            },
            {
                "date": "2026-01-20T10:52:56+03:00",
                "amount": 1.20,
                "description": "Компенсация комиссии за платёж",
            },
            {
                "date": "2026-01-20T10:52:47+03:00",
                "amount": 300.00,
                "description": "Регистрация платежа: СБП_Мой МТС",
            },
        ],
    },
    "79009876543": {
        "phone": "79009876543",
        "period_start": "2026-01-14T10:00:00+00:00",
        "period_end": "2026-02-13T10:00:00+00:00",
        "period_days": 30,
        "total_income": 1000.00,
        "total_expenses": 650.00,
        "period_balance_change": 350.00,
        "currency": "RUB",
        "income_by_category": [
            {"category": "Платёж", "amount": 1000.00},
        ],
        "expenses_by_category": [
            {"category": "Абонентская плата", "amount": 650.00},
        ],
        "transactions": [
            {
                "date": "2026-02-01T03:00:00+03:00",
                "amount": -650.00,
                "description": "Ежемесячная плата Тарифище",
            },
            {
                "date": "2026-01-25T14:30:00+03:00",
                "amount": 1000.00,
                "description": "Регистрация платежа: Банковская карта",
            },
        ],
    },
    "79005551234": {
        "phone": "79005551234",
        "period_start": "2026-01-14T12:00:00+00:00",
        "period_end": "2026-02-13T12:00:00+00:00",
        "period_days": 30,
        "total_income": 0.00,
        "total_expenses": 215.20,
        "period_balance_change": -215.20,
        "currency": "RUB",
        "income_by_category": [],
        "expenses_by_category": [
            {"category": "Абонентская плата", "amount": 200.00},
            {"category": "Дополнительные услуги", "amount": 15.20},
        ],
        "transactions": [
            {
                "date": "2026-01-28T03:00:00+03:00",
                "amount": -200.00,
                "description": "Ежемесячная плата НЕТАРИФ Junior",
            },
            {
                "date": "2026-01-30T11:00:00+03:00",
                "amount": -15.20,
                "description": "Подписка МТС Premium (контентная)",
            },
        ],
    },
}
