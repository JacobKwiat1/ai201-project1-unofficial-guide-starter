"""Scrape RateMyProfessors reviews into plain-text documents for the RAG pipeline.

RMP is a React SPA — the reviews are NOT in the page HTML. They're served by a
GraphQL endpoint, so we query that directly. The numeric id in each professor URL
(e.g. .../professor/2239018) maps to a relay node id of base64("Teacher-<id>").

Writes one .txt file per professor into documents/, formatted for chunking:
a short header block followed by one block per review.

Usage:  python scrape_rmp.py
"""

import base64
import html
import json
import re
import time
import urllib.request
from pathlib import Path

GRAPHQL_URL = "https://www.ratemyprofessors.com/graphql"
# Public basic-auth token shipped in RMP's own frontend bundle (not a secret).
AUTH = "Basic dGVzdDp0ZXN0"
OUT_DIR = Path(__file__).parent / "documents"

QUERY = """
query Prof($id: ID!) {
  node(id: $id) {
    ... on Teacher {
      firstName lastName department avgRating numRatings
      wouldTakeAgainPercent avgDifficulty
      school { name }
      ratings(first: 1000) {
        edges { node {
          class date helpfulRating difficultyRating clarityRating
          comment ratingTags wouldTakeAgain grade attendanceMandatory
          isForOnlineClass
        } }
      }
    }
  }
}
"""


def fetch_professor(numeric_id: str) -> dict:
    node_id = base64.b64encode(f"Teacher-{numeric_id}".encode()).decode()
    body = json.dumps({"query": QUERY, "variables": {"id": node_id}}).encode()
    req = urllib.request.Request(
        GRAPHQL_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": AUTH,
            "User-Agent": "Mozilla/5.0",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())["data"]["node"]


def format_professor(t: dict, source_url: str) -> str:
    name = f"{t['firstName']} {t['lastName']}".strip()
    lines = [
        f"Source URL: {source_url}",
        f"Professor: {name}",
        f"Department: {t.get('department') or 'N/A'}",
        f"School: {(t.get('school') or {}).get('name', 'N/A')}",
        f"Overall rating: {t.get('avgRating')} / 5  "
        f"(from {t.get('numRatings')} ratings)",
        f"Average difficulty: {t.get('avgDifficulty')} / 5",
        f"Would take again: {t.get('wouldTakeAgainPercent')}%",
        "",
        "=" * 60,
        "STUDENT REVIEWS",
        "=" * 60,
        "",
    ]
    seen = set()
    for edge in t["ratings"]["edges"]:
        r = edge["node"]
        # RMP's paginated API returns overlapping/duplicate edges, so skip any
        # review we've already emitted (keyed on class + date + comment).
        sig = (r.get("class"), r.get("date"), r.get("comment"))
        if sig in seen:
            continue
        seen.add(sig)
        # RMP returns HTML-escaped text (&amp;, &quot;, smart quotes) — decode it
        # so neither the embeddings nor cited quotes carry raw entities.
        comment = html.unescape((r.get("comment") or "").strip())
        tags = html.unescape((r.get("ratingTags") or "").replace("--", ", ").strip(", "))
        lines += [
            f"Class: {r.get('class') or 'N/A'}   Date: {(r.get('date') or '')[:10]}",
            f"Quality: {r.get('clarityRating')}/5   "
            f"Difficulty: {r.get('difficultyRating')}/5   "
            f"Would take again: {'yes' if r.get('wouldTakeAgain') else 'no'}   "
            f"Grade: {r.get('grade') or 'N/A'}",
            f"Tags: {tags}" if tags else "Tags: none",
            f"Comment: {comment}",
            "",
            "-" * 60,
            "",
        ]
    return "\n".join(lines)


def parse_planning(path: Path) -> list[tuple[str, str]]:
    """Pull (name, numeric_id) pairs out of the Documents table only.

    Scoped to the "## Documents" section so RMP URLs cited elsewhere (e.g. the
    Evaluation Plan questions) don't get scraped as bogus extra professors.
    Dedups by id in case the same professor is listed twice.
    """
    profs, seen = [], set()
    in_documents = False
    for line in path.read_text().splitlines():
        if line.startswith("## "):
            in_documents = line.strip().lower() == "## documents"
            continue
        if not in_documents:
            continue
        m = re.search(r"ratemyprofessors\.com/professor/(\d+)", line)
        if not m or m.group(1) in seen:
            continue
        seen.add(m.group(1))
        cells = [c.strip() for c in line.split("|")]
        name = cells[2] if len(cells) > 2 else m.group(1)
        name = name.replace(" ratemyprofessor", "")
        profs.append((name, m.group(1)))
    return profs


def safe_filename(name: str, numeric_id: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return f"{slug}_{numeric_id}.txt"


def main():
    OUT_DIR.mkdir(exist_ok=True)
    profs = parse_planning(Path(__file__).parent / "planning.md")
    print(f"Found {len(profs)} professors in planning.md\n")

    for name, numeric_id in profs:
        try:
            t = fetch_professor(numeric_id)
            if not t:
                print(f"  SKIP {name} ({numeric_id}): no data returned")
                continue
            source_url = f"https://www.ratemyprofessors.com/professor/{numeric_id}"
            text = format_professor(t, source_url)
            out = OUT_DIR / safe_filename(name, numeric_id)
            out.write_text(text, encoding="utf-8")
            n = len(t["ratings"]["edges"])
            print(f"  OK   {name}: {n} reviews -> {out.name}")
        except Exception as e:
            print(f"  FAIL {name} ({numeric_id}): {e}")
        time.sleep(1)  # be polite to the API


if __name__ == "__main__":
    main()
