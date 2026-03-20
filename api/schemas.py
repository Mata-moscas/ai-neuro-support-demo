"""Pydantic-схемы запросов и ответов API."""

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., description="Текст вопроса клиента")
    phone_number: str = Field(..., description="Номер телефона клиента (например, 79001234567)")
    response_format: str = Field(default="text", description="Формат ответа: 'text' или 'json'")


class ContinueRequest(BaseModel):
    message: str = Field(..., description="Сообщение от оператора поддержки")
    conversation_id: str = Field(..., description="ID предыдущего ответа для продолжения диалога")


class AgentResponse(BaseModel):
    answer: str = Field(..., description="Текст ответа агента")
    steps: list[dict] = Field(default_factory=list, description="Промежуточные шаги агента")
    response_id: str | None = Field(None, description="ID ответа для продолжения диалога")
