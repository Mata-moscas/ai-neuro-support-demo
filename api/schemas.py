"""Pydantic-схемы запросов и ответов API."""

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """Запрос к агенту поддержки."""
    question: str = Field(..., description="Текст вопроса клиента")
    phone_number: str = Field(..., description="Номер телефона клиента (например, 79001234567)")
    response_format: str = Field(
        default="text",
        description="Формат ответа: 'text' (черновик для оператора) или 'json' (для НейроСаппорт)",
    )


class AskResponse(BaseModel):
    """Ответ агента поддержки."""
    answer: str = Field(..., description="Текст ответа агента")
    scenario: str | None = Field(None, description="Определённый сценарий обработки")
    format: str = Field("text", description="Формат ответа")
    phone_number: str = Field(..., description="Номер телефона клиента")
    conversation_id: str = Field(..., description="ID диалога для продолжения")


class ContinueRequest(BaseModel):
    """Продолжение диалога (уточняющие вопросы оператора)."""
    message: str = Field(..., description="Сообщение от оператора поддержки")


class ContinueResponse(BaseModel):
    """Ответ агента на уточняющий вопрос."""
    answer: str = Field(..., description="Текст ответа агента")
    phone_number: str = Field(..., description="Номер телефона клиента")
    conversation_id: str = Field(..., description="ID диалога")


class HealthResponse(BaseModel):
    """Статус здоровья сервиса."""
    status: str
    tools_count: int
    scenarios_count: int
