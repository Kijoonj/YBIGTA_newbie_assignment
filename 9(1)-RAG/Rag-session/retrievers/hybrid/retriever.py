"""Hybrid retriever using Elasticsearch RRF (Reciprocal Rank Fusion).

Combines BM25 text search with dense vector kNN search.
Uses ES 8.14+ RRF support.
"""

import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

from ingest.embedding import embed_query

load_dotenv()

INDEX_NAME = "wiki-hybrid"


def get_es_client() -> Elasticsearch:
    return Elasticsearch(
        os.getenv("ELASTIC_ENDPOINT"),
        api_key=os.getenv("ELASTIC_API_KEY"),
        request_timeout=30,
    )


def search(query: str, top_k: int = 10, candidate_size: int = 50) -> list[dict]:
    """RRF hybrid search combining BM25 + kNN."""
    
    # 1. Generate Query Vector
    query_vector = embed_query(query)
    
    es = get_es_client()
    
    # 2. Construct RRF Query
    # Note: "window_size" is now "rank_window_size" in newer ES versions
    retriever_config = {
        "rrf": {
            "retrievers": [
                # Standard BM25 Retriever
                {
                    "standard": {
                        "query": {
                            "match": {
                                "text": query
                            }
                        }
                    }
                },
                # kNN Vector Retriever
                {
                    "knn": {
                        "field": "embedding",
                        "query_vector": query_vector,
                        "k": candidate_size,
                        "num_candidates": candidate_size * 2
                    }
                }
            ],
            "rank_constant": 60,
            "rank_window_size": top_k  # <--- FIXED HERE
        }
    }

    # 3. Execute Search
    response = es.search(
        index=INDEX_NAME,
        retriever=retriever_config,
        size=top_k,
        source_excludes=["embedding"]
    )
    
    # 4. Format Results
    results = []
    for hit in response["hits"]["hits"]:
        results.append({
            "id": hit["_id"],
            "text": hit["_source"]["text"],
            "score": hit["_score"],
            "method": "Hybrid (RRF)"
        })
        
    return results