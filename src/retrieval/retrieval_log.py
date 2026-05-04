# src/retrieval/retrieval_log.py
# Week 10 — Stage 2 evidence builder
#
# Runs 10 Wk9 questions through the dense retriever.
# Saves retrieval_log.json and retrieval_misses.md

import json
from src.retrieval.vector_store import VectorStore

WK9_QUESTIONS = [
    "What is force?",
    "What are the effects of force on an object?",
    "What is Newton's First Law of Motion?",
    "What is inertia?",
    "What is momentum?",
    "State Newton's Second Law of Motion.",
    "What is the formula for force according to Newton's Second Law?",
    "What is Newton's Third Law of Motion?",
    "What is action and reaction?",
    "Why does a passenger fall forward when a moving bus stops suddenly?",
]


def build_retrieval_log(store: VectorStore, k: int = 5) -> list:
    log = []
    for q in WK9_QUESTIONS:
        results = store.retrieve(q, k=k)
        top1 = results[0] if results else {}
        log.append({
            "question":      q,
            "top1_chunk_id": top1.get("chunk_id", ""),
            "top1_score":    top1.get("score", 0),
            "top1_text":     top1.get("text", "")[:300],
            "top1_relevant": None,     # fill manually: YES or NO
            "top_k_ids":     [r["chunk_id"] for r in results],
        })
        print(f"Q: {q}")
        print(f"  Top-1: [{top1.get('chunk_id','')}] score={top1.get('score',0)}")
        print(f"  {top1.get('text','')[:100]}...\n")

    with open("retrieval_log.json", "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)
    print("Saved retrieval_log.json")
    return log


def build_retrieval_misses_md(log: list):
    """
    After manually filling top1_relevant YES/NO in retrieval_log.json,
    run this to generate retrieval_misses.md for the 3 worst failures.
    """
    misses = [r for r in log if r.get("top1_relevant") == "NO"][:3]

    lines = ["# Retrieval Misses\n"]
    lines.append(
        "Top-1 retrieval was wrong for the following queries. "
        "Each miss is diagnosed into one of: chunking miss / embedding limitation / bad ranking.\n"
    )

    for m in misses:
        lines.append(f"## Query: {m['question']}\n")
        lines.append(f"**Top-1 chunk_id**: `{m['top1_chunk_id']}` (score: {m['top1_score']})\n")
        lines.append(f"**Top-1 text (first 300 chars)**:\n```\n{m['top1_text']}\n```\n")
        lines.append("**Diagnosis**: _[fill in: chunking miss / embedding limitation / bad ranking — explain why]_\n\n")

    with open("retrieval_misses.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("Saved retrieval_misses.md")


if __name__ == "__main__":
    store = VectorStore()
    log = build_retrieval_log(store)
    # After manually marking top1_relevant, run:
    # build_retrieval_misses_md(log)
