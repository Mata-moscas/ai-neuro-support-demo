"""FastAPI-приложение — REST API агента поддержки."""

import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from agent.main import Conversation, SupportAgent
from api.schemas import (
    AskRequest,
    AskResponse,
    ContinueRequest,
    ContinueResponse,
    HealthResponse,
)
from vector_store.indexer import index as index_scenarios
from vector_store.searcher import ScenarioSearcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Хранилище диалогов (в памяти; для продакшена — Redis/DB)
conversations: dict[str, Conversation] = {}
agent: SupportAgent | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация при старте: индексация сценариев, подключение к MCP."""
    global agent

    # Индексация Vector Store (если ещё не проиндексировано)
    logger.info("Indexing scenarios...")
    try:
        count = index_scenarios()
        logger.info(f"Indexed {count} scenarios")
    except Exception as e:
        logger.error(f"Failed to index scenarios: {e}")

    # Инициализация агента
    logger.info("Initializing agent...")
    agent = SupportAgent()
    await agent.initialize()
    logger.info("Agent ready")

    yield

    logger.info("Shutting down")


app = FastAPI(
    title="AI Neuro Support Agent",
    description="Агент-ассистент поддержки клиентов телеком-оператора",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
async def health():
    """Проверка состояния сервиса."""
    try:
        searcher = ScenarioSearcher()
        scenarios_count = searcher._collection.count()
    except Exception:
        scenarios_count = 0

    return HealthResponse(
        status="ok" if agent else "not_initialized",
        tools_count=len(agent._tools) if agent else 0,
        scenarios_count=scenarios_count,
    )


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    """Основной эндпоинт: задать вопрос агенту.

    Агент классифицирует обращение, собирает данные и формирует ответ.
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    result, conv = await agent.ask(
        question=request.question,
        phone_number=request.phone_number,
        response_format=request.response_format,
    )

    conversation_id = str(uuid.uuid4())
    conversations[conversation_id] = conv

    return AskResponse(
        answer=result["answer"],
        scenario=result.get("scenario"),
        format=result["format"],
        phone_number=result["phone_number"],
        conversation_id=conversation_id,
    )


@app.post("/ask/{conversation_id}", response_model=ContinueResponse)
async def continue_conversation(conversation_id: str, request: ContinueRequest):
    """Продолжить диалог с агентом (уточняющие вопросы оператора)."""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    conv = conversations.get(conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    result = await agent.continue_conversation(
        message=request.message,
        conversation=conv,
    )

    return ContinueResponse(
        answer=result["answer"],
        phone_number=result["phone_number"],
        conversation_id=conversation_id,
    )
