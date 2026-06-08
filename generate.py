"""Grounded generation stage for the RAG pipeline.

Retrieves the top-k chunks (rag_index.retrieve) and asks a Groq-hosted LLM to
answer using ONLY those chunks, citing the source URLs. Grounding is enforced two
ways (see planning.md / README — Grounded Generation):

  1. System prompt: the model is told to answer strictly from the provided
     reviews and to say it has no information when the answer isn't there — so a
     question about a professor not in the corpus (e.g. "Clark Kent") is refused
     rather than hallucinated.
  2. Structure: each chunk is passed with its source URL in a [Source: ...] tag,
     so the model can attribute claims and we can show the URLs to the user.

Usage:
    python generate.py "how hard are Mira Kim's classes?"
    python generate.py            # runs the 5 planning.md eval questions
    from generate import answer
    print(answer("does Kanika Sood assign a lot of homework?")["text"])
"""

import os
import sys

from dotenv import load_dotenv
from groq import Groq

from rag_index import retrieve, TOP_K

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# llama-3.3-70b is a strong, free Groq model; override with GROQ_MODEL in .env.
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

SYSTEM_PROMPT = """You are an assistant that answers questions about California \
State University, Fullerton computer science professors using ONLY the student \
reviews provided in the context below.

Rules:
- Use only information found in the provided reviews. Do not use outside knowledge.
- If the context does not contain the answer — including questions about a \
professor who does not appear in the reviews — say you don't have information \
about that in the reviews. Do not guess or invent professors, classes, or facts.
- When you answer from the reviews, cite the source URL(s) you used, formatted \
as a "Sources:" list at the end. If you don't have the information, say so plainly \
and do NOT include a Sources list.
- Be concise and specific. When useful, mention how many reviews support a point."""


def _client() -> Groq:
    return Groq(api_key=os.environ["GROQ_API_KEY"])


def format_context(chunks: list[dict]) -> str:
    """Render retrieved chunks into a numbered, source-tagged context block."""
    blocks = []
    for i, c in enumerate(chunks, 1):
        m = c["metadata"]
        if m["type"] == "review":
            head = f"{m['professor']} — {m.get('class', 'N/A')} (review on {m.get('date', 'n/a')})"
        else:
            head = f"{m['professor']} — overall profile"
        blocks.append(
            f"[{i}] Source: {head} | {m['source_url']}\n{c['text']}"
        )
    return "\n\n".join(blocks)


def answer(question: str, k: int = TOP_K) -> dict:
    """Retrieve, build a grounded prompt, and generate. Returns
    {"text", "chunks", "sources"}."""
    chunks = retrieve(question, k=k)
    context = format_context(chunks)
    user_msg = (
        f"Context (student reviews):\n\n{context}\n\n"
        f"Question: {question}"
    )
    resp = _client().chat.completions.create(
        model=GROQ_MODEL,
        temperature=0,  # deterministic, factual answers
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
    )
    # Unique source URLs in retrieval order, for the caller's convenience.
    sources, seen = [], set()
    for c in chunks:
        url = c["metadata"]["source_url"]
        if url not in seen:
            seen.add(url)
            sources.append(url)
    return {"text": resp.choices[0].message.content, "chunks": chunks, "sources": sources}


EVAL_QUESTIONS = [
    "What do students say about Anand Panangadan's CPSC 481?",
    "Does Kanika Sood assign a lot of homework?",
    "How hard are Mira Kim's classes?",
    "What are some complaints students have about Paul Inventado?",
    "How hard is Clark Kent's class?",
]


if __name__ == "__main__":
    questions = [" ".join(sys.argv[1:])] if len(sys.argv) > 1 else EVAL_QUESTIONS
    for q in questions:
        print("=" * 70)
        print(f"Q: {q}\n")
        result = answer(q)
        print(result["text"])
        print()
