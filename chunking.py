"""Chunk the scraped RateMyProfessors documents for the RAG pipeline.

Strategy (see planning.md — Chunking Strategy):
  - One chunk per review. Reviews are RMP's atomic unit and are hard-capped at
    ~350 chars, so they never need splitting and overlap would only bleed one
    student's words into another's chunk. No fixed-size windowing, no overlap.
  - One extra "summary" chunk per professor holding the file header (aggregate
    rating, difficulty, would-take-again %), so aggregate questions
    ("what's Choi's overall rating?") retrieve cleanly instead of guessing from
    a handful of individual reviews.

Each chunk's embedded TEXT carries the professor name + class + tags + comment so
name-based queries can match. Everything needed for filtering and citation
(URL, professor, class, quality, difficulty, date, tags) lives in METADATA, kept
out of the embedded text where a raw URL or rating number would only add noise.

Usage:
    from chunking import load_chunks
    chunks = load_chunks()          # list of {"id", "text", "metadata"}
or run directly to see stats:
    python chunking.py
"""

import glob
import os
import re

DOCS_DIR = os.path.join(os.path.dirname(__file__), "documents")
REVIEW_SEP = "-" * 60

HEADER_FIELDS = [
    "Source URL", "Professor", "Department", "School",
    "Overall rating", "Average difficulty", "Would take again",
]


def _parse_header(header: str) -> dict:
    fields = {}
    for key in HEADER_FIELDS:
        m = re.search(rf"{re.escape(key)}:\s*(.+)", header)
        fields[key] = m.group(1).strip() if m else None
    return fields


def _parse_review(block: str) -> dict:
    cls = re.search(r"Class:\s*(.+?)\s{2,}Date:\s*(\S+)", block)
    quality = re.search(r"Quality:\s*([0-9.]+)/5", block)
    difficulty = re.search(r"Difficulty:\s*([0-9.]+)/5", block)
    wta = re.search(r"Would take again:\s*(yes|no)", block)
    tags = re.search(r"Tags:\s*(.+)", block)
    comment = block.split("Comment:", 1)[1].strip() if "Comment:" in block else ""
    return {
        "class": cls.group(1).strip() if cls else "N/A",
        "date": cls.group(2).strip() if cls else "",
        "quality": float(quality.group(1)) if quality else -1.0,
        "difficulty": float(difficulty.group(1)) if difficulty else -1.0,
        "would_take_again": (wta.group(1) == "yes") if wta else False,
        "tags": tags.group(1).strip() if tags else "none",
        "comment": comment,
    }


def _parse_file(path: str):
    text = open(path, encoding="utf-8").read()
    header_part, _, body = text.partition("STUDENT REVIEWS")
    header_part = re.split(r"={5,}", header_part)[0].strip()
    fields = _parse_header(header_part)

    body = re.split(r"={5,}", body, maxsplit=1)[-1]
    reviews = [_parse_review(b) for b in body.split(REVIEW_SEP) if "Comment:" in b]
    return fields, header_part, reviews


def _review_text(professor: str, r: dict) -> str:
    text = f"Professor {professor} (class {r['class']}). "
    if r["tags"].lower() != "none":
        text += f"Tags: {r['tags']}. "
    text += r["comment"]
    return text.strip()


def _summary_text(header_part: str) -> str:
    # Drop the Source URL line (it lives in metadata); keep the rest verbatim.
    lines = [ln for ln in header_part.splitlines() if not ln.startswith("Source URL:")]
    return "\n".join(lines).strip()


def load_chunks(docs_dir: str = DOCS_DIR) -> list[dict]:
    """Return a list of {"id", "text", "metadata"} chunks across all documents."""
    chunks = []
    for path in sorted(glob.glob(os.path.join(docs_dir, "*.txt"))):
        stem = os.path.splitext(os.path.basename(path))[0]
        fields, header_part, reviews = _parse_file(path)
        url = fields["Source URL"]
        professor = fields["Professor"]

        # Summary chunk (one per professor) — the file header.
        chunks.append({
            "id": f"{stem}-summary",
            "text": _summary_text(header_part),
            "metadata": {
                "type": "summary",
                "source_url": url,
                "professor": professor,
            },
        })

        # One chunk per review.
        for i, r in enumerate(reviews):
            chunks.append({
                "id": f"{stem}-r{i}",
                "text": _review_text(professor, r),
                "metadata": {
                    "type": "review",
                    "source_url": url,
                    "professor": professor,
                    "class": r["class"],
                    "quality": r["quality"],
                    "difficulty": r["difficulty"],
                    "date": r["date"],
                    "tags": r["tags"],
                },
            })
    return chunks


if __name__ == "__main__":
    chunks = load_chunks()
    n_summary = sum(c["metadata"]["type"] == "summary" for c in chunks)
    n_review = sum(c["metadata"]["type"] == "review" for c in chunks)
    print(f"{len(chunks)} chunks total: {n_summary} summary + {n_review} review\n")

    summary = next(c for c in chunks if c["metadata"]["type"] == "summary")
    review = next(c for c in chunks if c["metadata"]["type"] == "review")
    for label, c in [("SUMMARY", summary), ("REVIEW", review)]:
        print(f"--- {label} chunk: {c['id']} ---")
        print("metadata:", c["metadata"])
        print("text:", repr(c["text"][:300]))
        print()
