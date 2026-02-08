"""Ingest embeddings into Pinecone vector index.

Batch upsert: 100 vectors per call.
Metadata: text truncated to 1000 chars (40KB limit).
"""

import json
import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from pinecone import Pinecone
from tqdm import tqdm

load_dotenv()

RAW_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "processed"

BATCH_SIZE = 100
TEXT_LIMIT = 1000  # metadata text truncation


def ingest(progress_callback=None):
    """Batch upsert embeddings into Pinecone vector index.

    Args:
        progress_callback: Optional callback(current, total) for progress updates.

    Returns:
        int: Number of vectors upserted.

    Hints:
        - Load embeddings from PROCESSED_DIR / "embeddings.npy"
        - Load IDs from PROCESSED_DIR / "embedding_ids.json"
        - Load texts from RAW_DIR / "corpus.jsonl" for metadata
        - Connect: Pinecone(api_key=...) → pc.Index(index_name)
        - Upsert format: {"id": ..., "values": [...], "metadata": {"text": ...}}
        - Batch size: BATCH_SIZE (100), truncate text to TEXT_LIMIT (1000) chars
    """
    # 1. Load Data
    emb_path = PROCESSED_DIR / "embeddings.npy"
    ids_path = PROCESSED_DIR / "embedding_ids.json"
    corpus_path = RAW_DIR / "corpus.jsonl"

    if not emb_path.exists() or not ids_path.exists():
        print("Embeddings not found. Run ingest/embedding.py first.")
        return 0

    print("Loading data...")
    embeddings = np.load(emb_path)
    ids = json.loads(ids_path.read_text(encoding="utf-8"))

    # Load corpus text into a lookup dict for fast metadata matching
    # Map: id -> text
    id_to_text = {}
    with open(corpus_path, encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            id_to_text[doc["id"]] = doc["text"]

    # 2. Initialize Pinecone
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX_NAME")
    index = pc.Index(index_name)

    # 3. Batch Upsert
    total_vectors = len(ids)
    vectors_to_upsert = []
    
    # Using tqdm for progress bar
    pbar = tqdm(total=total_vectors, desc="Upserting to Pinecone")

    count = 0
    for i, doc_id in enumerate(ids):
        # Prepare vector tuple: (id, values, metadata)
        text = id_to_text.get(doc_id, "")
        
        # Truncate text for metadata
        if len(text) > TEXT_LIMIT:
            text = text[:TEXT_LIMIT]

        vector_data = {
            "id": doc_id,
            "values": embeddings[i].tolist(),
            "metadata": {"text": text}
        }
        vectors_to_upsert.append(vector_data)

        # Upsert when batch is full or at the end
        if len(vectors_to_upsert) >= BATCH_SIZE or i == total_vectors - 1:
            try:
                index.upsert(vectors=vectors_to_upsert)
                count += len(vectors_to_upsert)
                pbar.update(len(vectors_to_upsert))
                
                if progress_callback:
                    progress_callback(count, total_vectors)
                    
            except Exception as e:
                print(f"Error upserting batch: {e}")
            
            vectors_to_upsert = [] # Reset batch

    pbar.close()
    return count


if __name__ == "__main__":
    ingest()
