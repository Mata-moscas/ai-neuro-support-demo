"""Мок-данные подписок клиентов."""

SUBSCRIPTIONS = {
    "79001234567": {
        "phone": "79001234567",
        "data_as_of": "2026-02-13T08:36:36+00:00",
        "subscriptions": [],
    },
    "79009876543": {
        "phone": "79009876543",
        "data_as_of": "2026-02-13T10:30:00+00:00",
        "subscriptions": [
            {
                "name": "МТС Premium",
                "type": "Контентная",
                "price": 299.00,
                "currency": "RUB",
                "billing_period": "Месяц",
                "activated_at": "2025-08-15T10:00:00+03:00",
                "next_charge_date": "2026-03-01T00:00:00+03:00",
                "status": "Активна",
                "description": "Подписка на музыку, кино, книги и кешбэк",
            },
            {
                "name": "KION",
                "type": "Контентная",
                "price": 199.00,
                "currency": "RUB",
                "billing_period": "Месяц",
                "activated_at": "2025-11-01T12:00:00+03:00",
                "next_charge_date": "2026-03-01T00:00:00+03:00",
                "status": "Активна",
                "description": "Онлайн-кинотеатр KION",
            },
        ],
    },
    "79005551234": {
        "phone": "79005551234",
        "data_as_of": "2026-02-13T12:15:00+00:00",
        "subscriptions": [
            {
                "name": "МТС Premium",
                "type": "Контентная",
                "price": 15.20,
                "currency": "RUB",
                "billing_period": "Ежедневно",
                "activated_at": "2026-01-10T09:00:00+03:00",
                "next_charge_date": "2026-02-14T00:00:00+03:00",
                "status": "Активна",
                "description": "Подписка МТС Premium (ежедневное списание)",
            },
        ],
    },
}
