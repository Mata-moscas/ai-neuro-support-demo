#!/usr/bin/env python3
"""Загрузка сценариев из Instructions.json в Yandex AI Studio Vector Store.

Скрипт:
1. Читает Instructions.json
2. Разбивает на отдельные файлы по сценариям
3. Загружает каждый файл через Files API
4. Создаёт Vector Store (поисковый индекс) со всеми файлами

Использование:
    export YC_API_KEY=<ваш_api_ключ>
    export YC_FOLDER_ID=<id_каталога>
    python -m setup.upload_scenarios [--instructions path/to/Instructions.json]
"""

import argparse
import io
import json
import os
import sys
import time

import openai


YC_API_KEY = os.getenv("YC_API_KEY", "")
YC_FOLDER_ID = os.getenv("YC_FOLDER_ID", "")
YC_BASE_URL = os.getenv("YC_BASE_URL", "https://ai.api.cloud.yandex.net/v1")

DEFAULT_INSTRUCTIONS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "materials", "Instructions.json"
)


def get_client() -> openai.OpenAI:
    if not YC_API_KEY:
        sys.exit("Error: YC_API_KEY environment variable is required")
    if not YC_FOLDER_ID:
        sys.exit("Error: YC_FOLDER_ID environment variable is required")

    return openai.OpenAI(
        api_key=YC_API_KEY,
        base_url=YC_BASE_URL,
        project=YC_FOLDER_ID,
    )


def load_instructions(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def upload_scenarios(client: openai.OpenAI, instructions: list[dict]) -> list[str]:
    """Загрузить каждый сценарий как отдельный файл. Возвращает список file_id."""
    file_ids = []

    for i, item in enumerate(instructions):
        title = item.get("title", f"Сценарий {i}")
        content = item.get("content", "")
        code = item.get("code", f"scenario_{i}")

        if len(content.strip()) < 10:
            print(f"  [{i+1}/{len(instructions)}] Skip (too short): {title[:60]}")
            continue

        # Формируем текстовый файл
        text = f"# {title}\n\nКод сценария: {code}\n\n{content}"
        filename = f"scenario_{code}.txt"

        file_bytes = text.encode("utf-8")
        file_obj = io.BytesIO(file_bytes)

        try:
            uploaded = client.files.create(
                file=(filename, file_obj),
                purpose="assistants",
            )
            file_ids.append(uploaded.id)
            print(f"  [{i+1}/{len(instructions)}] Uploaded: {title[:60]} -> {uploaded.id}")
        except Exception as e:
            print(f"  [{i+1}/{len(instructions)}] ERROR uploading {title[:60]}: {e}")

        # Небольшая пауза чтобы не превысить rate limit
        if (i + 1) % 10 == 0:
            time.sleep(1)

    return file_ids


def create_vector_store(client: openai.OpenAI, file_ids: list[str], name: str) -> str:
    """Создать Vector Store с загруженными файлами. Возвращает vector_store_id."""
    print(f"\nCreating vector store '{name}' with {len(file_ids)} files...")

    vector_store = client.vector_stores.create(
        name=name,
        file_ids=file_ids,
    )

    print(f"Vector Store created: {vector_store.id}")
    print(f"Status: {vector_store.status}")

    # Ждём пока индексация завершится
    while vector_store.status == "in_progress":
        print("  Indexing in progress...")
        time.sleep(5)
        vector_store = client.vector_stores.retrieve(vector_store.id)

    print(f"Final status: {vector_store.status}")
    print(f"Files: {vector_store.file_counts}")

    return vector_store.id


def main():
    parser = argparse.ArgumentParser(description="Upload scenarios to Yandex AI Studio Vector Store")
    parser.add_argument(
        "--instructions",
        default=DEFAULT_INSTRUCTIONS_PATH,
        help="Path to Instructions.json",
    )
    parser.add_argument(
        "--name",
        default="support_scenarios",
        help="Name for the Vector Store",
    )
    args = parser.parse_args()

    client = get_client()

    print(f"Loading instructions from {args.instructions}...")
    instructions = load_instructions(args.instructions)
    print(f"Loaded {len(instructions)} scenarios\n")

    print("Uploading scenario files...")
    file_ids = upload_scenarios(client, instructions)
    print(f"\nUploaded {len(file_ids)} files\n")

    if not file_ids:
        sys.exit("No files uploaded. Exiting.")

    vs_id = create_vector_store(client, file_ids, args.name)

    print(f"\n{'='*60}")
    print(f"Vector Store ID: {vs_id}")
    print(f"{'='*60}")
    print(f"\nДобавьте в .env:\n  VECTOR_STORE_ID={vs_id}")


if __name__ == "__main__":
    main()
