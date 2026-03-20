"""Поиск релевантных сценариев в ChromaDB по тексту запроса."""

import os

import chromadb
from chromadb.config import Settings

COLLECTION_NAME = "support_scenarios"
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")


class ScenarioSearcher:
    def __init__(self, persist_dir: str | None = None):
        self._persist_dir = persist_dir or CHROMA_PERSIST_DIR
        self._client = chromadb.PersistentClient(
            path=self._persist_dir,
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_collection(name=COLLECTION_NAME)

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """Найти top_k наиболее релевантных сценариев по запросу.

        Args:
            query: Текст запроса клиента.
            top_k: Количество возвращаемых результатов.

        Returns:
            Список словарей с ключами: title, code, content, distance.
        """
        results = self._collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        scenarios = []
        for i in range(len(results["ids"][0])):
            scenarios.append({
                "id": results["ids"][0][i],
                "title": results["metadatas"][0][i].get("title", ""),
                "code": results["metadatas"][0][i].get("code", ""),
                "content": results["documents"][0][i],
                "distance": results["distances"][0][i],
            })

        return scenarios
