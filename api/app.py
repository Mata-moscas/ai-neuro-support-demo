"""FastAPI-приложение — REST API + веб-интерфейс агента поддержки."""

import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from agent.config import YC_API_KEY, VECTOR_STORE_ID
from agent.main import continue_dialog, get_client, process_question
from api.schemas import AgentResponse, AskRequest, ContinueRequest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Neuro Support Agent",
    description="Агент-ассистент поддержки клиентов телеком-оператора",
    version="0.2.0",
)

# Раздача статических файлов (веб-интерфейс)
WEB_DIR = os.path.join(os.path.dirname(__file__), "..", "web")


@app.get("/")
async def index():
    """Главная страница — веб-интерфейс чат-бота."""
    return FileResponse(os.path.join(WEB_DIR, "index.html"))


@app.get("/health")
async def health():
    """Проверка состояния сервиса."""
    return {
        "status": "ok",
        "api_key_set": bool(YC_API_KEY),
        "vector_store_id": VECTOR_STORE_ID or "not configured",
    }


@app.post("/api/ask", response_model=AgentResponse)
async def ask(request: AskRequest):
    """Основной эндпоинт: задать вопрос агенту.

    Агент ищет сценарий в Vector Store, собирает данные
    через function calling и формирует ответ.
    """
    if not YC_API_KEY:
        raise HTTPException(status_code=503, detail="YC_API_KEY not configured")

    try:
        client = get_client()
        result = process_question(
            client=client,
            question=request.question,
            phone_number=request.phone_number,
            response_format=request.response_format,
        )
        return AgentResponse(
            answer=result["answer"],
            steps=result["steps"],
            response_id=result["response_id"],
            model_outputs=result.get("model_outputs", []),
        )
    except Exception as e:
        logger.exception("Error processing question")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/continue", response_model=AgentResponse)
async def continue_conv(request: ContinueRequest):
    """Продолжить диалог с агентом (уточняющие вопросы оператора)."""
    if not YC_API_KEY:
        raise HTTPException(status_code=503, detail="YC_API_KEY not configured")

    try:
        client = get_client()
        result = continue_dialog(
            client=client,
            message=request.message,
            previous_response_id=request.conversation_id,
        )
        return AgentResponse(
            answer=result["answer"],
            steps=result["steps"],
            response_id=result["response_id"],
            model_outputs=result.get("model_outputs", []),
        )
    except Exception as e:
        logger.exception("Error continuing dialog")
        raise HTTPException(status_code=500, detail=str(e))
