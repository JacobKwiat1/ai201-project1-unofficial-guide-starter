"""Gradio query interface for The Unofficial Guide (Milestone 5).

A thin front door over the RAG pipeline: it calls generate.answer() and displays
the grounded response, the source URLs consulted, and the actual review chunks
that were retrieved — so the grounding and attribution are visible to whoever is
testing the system, not just claimed.

Run:
    python app.py
then open the printed http://127.0.0.1:7860 URL.
"""

import gradio as gr

from generate import answer, EVAL_QUESTIONS


def respond(question: str):
    if not question or not question.strip():
        return "Please enter a question.", "", ""

    result = answer(question)

    sources_md = "\n".join(f"- {u}" for u in result["sources"]) or "_None_"

    blocks = []
    for i, c in enumerate(result["chunks"], 1):
        m = c["metadata"]
        loc = m.get("class", "profile") if m["type"] == "review" else "overall profile"
        meta = f"_{m['type']} · {m['professor']} · {loc}"
        if m["type"] == "review":
            meta += f" · quality {m['quality']}/5 · difficulty {m['difficulty']}/5 · {m['date']}"
        meta += "_"
        blocks.append(f"**[{i}]** {meta}\n\n{c['text']}")
    retrieved_md = "\n\n---\n\n".join(blocks)

    return result["text"], sources_md, retrieved_md


with gr.Blocks(title="The Unofficial Guide") as demo:
    gr.Markdown(
        "# The Unofficial Guide\n"
        "Ask about CSUF computer science professors. Answers are grounded **only** "
        "in student reviews from RateMyProfessors — if the reviews don't cover it, "
        "the system says so rather than guessing."
    )

    with gr.Row():
        question = gr.Textbox(
            label="Your question",
            placeholder="e.g. How hard are Mira Kim's classes?",
            scale=4,
            autofocus=True,
        )
        ask = gr.Button("Ask", variant="primary", scale=1)

    answer_box = gr.Markdown(label="Answer")

    with gr.Accordion("Sources consulted", open=True):
        sources_box = gr.Markdown()
    with gr.Accordion("Retrieved reviews (what the answer is grounded in)", open=False):
        retrieved_box = gr.Markdown()

    gr.Examples(examples=[[q] for q in EVAL_QUESTIONS], inputs=question)

    ask.click(respond, inputs=question, outputs=[answer_box, sources_box, retrieved_box])
    question.submit(respond, inputs=question, outputs=[answer_box, sources_box, retrieved_box])


if __name__ == "__main__":
    demo.launch()
