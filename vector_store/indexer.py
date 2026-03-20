#!/usr/bin/env python3
"""Индексация сценариев из Instructions.json в ChromaDB."""

import json
import os
import sys

import chromadb
from chromadb.config import Settings


COLLECTION_NAME = "support_scenarios"
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")
INSTRUCTIONS_PATH = os.getenv(
    "INSTRUCTIONS_PATH",
    os.path.join(os.path.dirname(__file__), "..", "materials", "Instructions.json"),
)


def load_instructions(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def prepare_documents(instructions: list[dict]) -> tuple[list[str], list[dict], list[str]]:
    """Подготовить документы для индексации.

    Каждый сценарий превращается в документ из заголовка + контента.
    Метаданные сохраняются отдельно для последующего использования.
    """
    documents = []
    metadatas = []
    ids = []

    for i, item in enumerate(instructions):
        title = item.get("title", "")
        content = item.get("content", "")
        code = item.get("code", "")

        doc_text = f"{title}\n\n{content}"
        if len(doc_text.strip()) < 10:
            continue

        documents.append(doc_text)
        metadatas.append({
            "title": title,
            "code": code,
            "url": item.get("url", ""),
            "parent_url": item.get("parent_url", ""),
        })
        ids.append(f"scenario_{code}" if code else f"scenario_{i}")

    return documents, metadatas, ids


def index(instructions_path: str | None = None, persist_dir: str | None = None) -> int:
    """Проиндексировать сценарии в ChromaDB.

    Returns:
        Количество проиндексированных документов.
    """
    path = instructions_path or INSTRUCTIONS_PATH
    persist = persist_dir or CHROMA_PERSIST_DIR

    print(f"Loading instructions from {path}...")
    instructions = load_instructions(path)
    print(f"Loaded {len(instructions)} entries")

    documents, metadatas, ids = prepare_documents(instructions)
    print(f"Prepared {len(documents)} documents for indexing")

    client = chromadb.PersistentClient(
        path=persist,
        settings=Settings(anonymized_telemetry=False),
    )

    # Удаляем коллекцию если уже существует (переиндексация)
    try:
        client.delete_collection(COLLECTION_NAME)
    except ValueError:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # ChromaDB поддерживает батчи до 5461 документов
    batch_size = 500
    for start in range(0, len(documents), batch_size):
        end = min(start + batch_size, len(documents))
        collection.add(
            documents=documents[start:end],
            metadatas=metadatas[start:end],
            ids=ids[start:end],
        )
        print(f"  Indexed {end}/{len(documents)}")

    print(f"Indexing complete. Collection '{COLLECTION_NAME}' has {collection.count()} documents.")
    return collection.count()


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    index(instructions_path=path)
