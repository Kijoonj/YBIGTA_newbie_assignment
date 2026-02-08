"""Upstage Solar embedding utility with disk caching and parallel API keys."""

import json
import os
import time
import threading  # <--- Added
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

# <--- Added: Try to import Streamlit context helpers safely
try:
    from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

load_dotenv()

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
EMBEDDINGS_PATH = PROCESSED_DIR / "embeddings.npy"
IDS_PATH = PROCESSED_DIR / "embedding_ids.json"

BATCH_SIZE = 100
RPM_LIMIT = 100
MIN_INTERVAL = 60.0 / RPM_LIMIT
DIM = 4096
BASE_URL = "https://api.upstage.ai/v1/solar"
MAX_CHARS = 12000
MAX_RETRIES = 3


def _get_api_keys() -> list[str]:
    """Collect all UPSTAGE_API_KEY* from env."""
    keys = []
    for i in range(1, 100):
        key = os.getenv(f"UPSTAGE_API_KEY{i}")
        if key:
            keys.append(key.strip())
        else:
            break
    if not keys:
        single = os.getenv("UPSTAGE_API_KEY", "")
        if single:
            keys.append(single.strip())
    return keys


def _truncate(text: str) -> str:
    """Truncate text to stay within token limits."""
    if len(text) > MAX_CHARS:
        return text[:MAX_CHARS]
    return text


def _embed_batch_safe(client: OpenAI, batch: list[str]) -> list[list[float]]:
    """Embed a batch with retry and fallback to smaller sub-batches."""
    truncated = [_truncate(t) for t in batch]

    for attempt in range(MAX_RETRIES):
        try:
            response = client.embeddings.create(
                model="solar-embedding-1-large-passage",
                input=truncated,
            )
            sorted_data = sorted(response.data, key=lambda x: x.index)
            return [item.embedding for item in sorted_data]
        except Exception as e:
            err_msg = str(e)
            if "maximum context length" in err_msg or "4000 tokens" in err_msg:
                mid = len(truncated) // 2
                if mid == 0:
                    truncated = [t[:MAX_CHARS // 2] for t in truncated]
                    continue
                left = _embed_batch_safe(client, truncated[:mid])
                time.sleep(MIN_INTERVAL)
                right = _embed_batch_safe(client, truncated[mid:])
                return left + right
            elif attempt < MAX_RETRIES - 1:
                wait = 2 ** (attempt + 1)
                time.sleep(wait)
            else:
                raise e
    return []


def embed_passages(texts: list[str], ids: list[str], progress_callback=None) -> np.ndarray:
    """Embed passages using parallel API keys."""
    keys = _get_api_keys()
    if not keys:
        raise ValueError("No UPSTAGE_API_KEY found.")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    batches = []
    for i in range(0, len(texts), BATCH_SIZE):
        batches.append((i, texts[i : i + BATCH_SIZE]))

    tasks_per_key = [[] for _ in range(len(keys))]
    for i, batch in enumerate(batches):
        tasks_per_key[i % len(keys)].append(batch)

    final_embeddings = np.zeros((len(texts), DIM), dtype=np.float32)
    pbar = tqdm(total=len(texts), desc="Embedding")

    # <--- CRITICAL FIX: Capture the main thread's Streamlit context
    ctx = get_script_run_ctx() if STREAMLIT_AVAILABLE else None

    def worker(key_idx):
        # <--- CRITICAL FIX: Attach the context to this worker thread
        if STREAMLIT_AVAILABLE and ctx:
            add_script_run_ctx(threading.current_thread(), ctx)

        client = OpenAI(api_key=keys[key_idx], base_url=BASE_URL)
        my_tasks = tasks_per_key[key_idx]

        for start_idx, batch_texts in my_tasks:
            start_time = time.time()
            embeddings = _embed_batch_safe(client, batch_texts)

            for j, emb in enumerate(embeddings):
                if start_idx + j < len(texts):
                    final_embeddings[start_idx + j] = emb

            pbar.update(len(batch_texts))
            
            # Now this callback works because the thread has the Streamlit context
            if progress_callback:
                progress_callback(pbar.n, pbar.total)

            elapsed = time.time() - start_time
            if elapsed < MIN_INTERVAL:
                time.sleep(MIN_INTERVAL - elapsed)

    with ThreadPoolExecutor(max_workers=len(keys)) as executor:
        futures = [executor.submit(worker, i) for i in range(len(keys))]
        for f in as_completed(futures):
            f.result()

    pbar.close()

    print(f"Saving to {EMBEDDINGS_PATH}...")
    np.save(EMBEDDINGS_PATH, final_embeddings)
    with open(IDS_PATH, "w", encoding="utf-8") as f:
        json.dump(ids, f)

    return final_embeddings


def embed_query(query: str) -> list[float]:
    """Embed a single query using the query model."""
    keys = _get_api_keys()
    if not keys:
        raise ValueError("No UPSTAGE_API_KEY found.")

    client = OpenAI(api_key=keys[0], base_url=BASE_URL)
    response = client.embeddings.create(
        model="solar-embedding-1-large-query",
        input=_truncate(query)
    )
    return response.data[0].embedding


def load_cached_embeddings() -> tuple[np.ndarray, list[str]] | None:
    if EMBEDDINGS_PATH.exists() and IDS_PATH.exists():
        embeddings = np.load(EMBEDDINGS_PATH)
        ids = json.loads(IDS_PATH.read_text())
        return embeddings, ids
    return None


if __name__ == "__main__":
    from data.download import RAW_DIR

    corpus_path = RAW_DIR / "corpus.jsonl"
    if not corpus_path.exists():
        print("Run data/download.py first.")
        raise SystemExit(1)

    texts, ids = [], []
    with open(corpus_path, encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            ids.append(doc["id"])
            texts.append(doc["text"])

    embed_passages(texts, ids)