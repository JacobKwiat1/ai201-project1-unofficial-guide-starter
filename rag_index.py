"""Embedding + vector store + retrieval for the RAG pipeline.

Implements two of the planning.md pipeline stages:
  - Embedding + Vector Store: embed every chunk from chunking.load_chunks() with
    all-MiniLM-L6-v2 (sentence-transformers) and persist them in a local ChromaDB
    collection.
  - Retrieval: embed the query with the same model and return the top-k nearest
    chunks (top-k = 8, per planning.md — Retrieval Approach).

MiniLM is the right fit here: review chunks are ~120 tokens, so the 256-token
window never truncates, it runs locally for free, and it was trained on exactly
this kind of short-sentence text. No query prefix is needed (unlike BGE models).

Usage:
    python rag_index.py            # (re)build the index, then run a demo query
    from rag_index import retrieve
    hits = retrieve("how hard are Mira Kim's classes?")
"""

import os

import chromadb
from sentence_transformers import SentenceTransformer

from chunking import load_chunks

EMBED_MODEL = "all-MiniLM-L6-v2"   # planning.md — Retrieval Approach
TOP_K = 8                          # planning.md — Retrieval Approach
COLLECTION = "rmp_reviews"
DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")

_model = None
_client = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def _get_client() -> "chromadb.ClientAPI":
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=DB_PATH)
    return _client


def _embed(texts: list[str]) -> list[list[float]]:
    # Normalized vectors so the collection's cosine space behaves as expected.
    return _get_model().encode(
        texts, normalize_embeddings=True, show_progress_bar=False
    ).tolist()


def build_index(batch_size: int = 128) -> int:
    """Embed all chunks and (re)build the ChromaDB collection. Returns chunk count."""
    client = _get_client()
    # Start clean so re-runs don't duplicate or leave stale chunks behind.
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    collection = client.create_collection(
        name=COLLECTION, metadata={"hnsw:space": "cosine"}
    )

    chunks = load_chunks()
    print(f"Embedding {len(chunks)} chunks with {EMBED_MODEL} ...")
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start:start + batch_size]
        collection.add(
            ids=[c["id"] for c in batch],
            documents=[c["text"] for c in batch],
            metadatas=[c["metadata"] for c in batch],
            embeddings=_embed([c["text"] for c in batch]),
        )
        print(f"  indexed {min(start + batch_size, len(chunks))}/{len(chunks)}")
    return len(chunks)


def get_collection():
    return _get_client().get_collection(COLLECTION)


def retrieve(query: str, k: int = TOP_K, where: dict | None = None) -> list[dict]:
    """Return the top-k chunks for a query as a list of
    {"id", "text", "metadata", "distance"}, nearest first."""
    res = get_collection().query(
        query_embeddings=_embed([query]),
        n_results=k,
        where=where,
        include=["documents", "metadatas", "distances"],
    )
    return [
        {
            "id": res["ids"][0][i],
            "text": res["documents"][0][i],
            "metadata": res["metadatas"][0][i],
            "distance": res["distances"][0][i],
        }
        for i in range(len(res["ids"][0]))
    ]


if __name__ == "__main__":
    n = build_index()
    print(f"\nIndexed {n} chunks into '{COLLECTION}' at {DB_PATH}\n")

    demo = "how hard are Mira Kim's classes?"
    print(f"Demo query: {demo!r}\n")
    for h in retrieve(demo):
        m = h["metadata"]
        tag = m["type"]
        label = m.get("class", "—") if tag == "review" else "(professor summary)"
        print(f"[{h['distance']:.3f}] {m['professor']} {label} <{tag}>")
        print(f"        {h['text'][:140].replace(chr(10), ' ')}")
