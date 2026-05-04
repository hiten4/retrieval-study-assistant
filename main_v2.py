# main_v2.py
# ask(question) → {answer, sources, chunk_ids}
# Uses: mxbai-embed-large-v1 (local) + Groq llama-3.3-70b-versatile (free API)

import os
import sys
import json
from pathlib import Path

# ── Fix 1: load .env from project root explicitly ────────────────────────────
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

# ── Fix 2: add project root to sys.path ─────────────────────────────────────
PROJECT_ROOT = str(Path(__file__).resolve().parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.retrieval.vector_store import VectorStore
from src.generation.llm_v2 import LLMGeneratorV2

CHUNKS_PATH = "wk10_chunks.json"

_store     = None
_generator = None


def _init():
    global _store, _generator

    if _store is None:
        _store = VectorStore()

        # Warn early if chunks file is missing or has only 1 chunk
        if not os.path.exists(CHUNKS_PATH):
            raise FileNotFoundError(
                f"{CHUNKS_PATH} not found.\n"
                "Run Stage 1 in notebook.ipynb first to generate chunks."
            )
        with open(CHUNKS_PATH) as f:
            chunk_count = len(json.load(f))
        if chunk_count <= 1:
            raise ValueError(
                f"{CHUNKS_PATH} only has {chunk_count} chunk(s).\n"
                "Your PDF extraction or chunker produced only 1 chunk — check Stage 1.\n"
                "Also delete ./chroma_wk10_hf and re-run after fixing the chunks."
            )

        if _store.collection.count() == 0:
            _store.load_and_embed(CHUNKS_PATH)

    if _generator is None:
        _generator = LLMGeneratorV2(prompt_version="v2")


def ask(question: str, k: int = 5) -> dict:
    """Returns: {answer: str, sources: list[str], chunk_ids: list[str]}"""
    _init()
    chunks = _store.retrieve(question, k=k)

    print(f"\n[RETRIEVED] Top-{len(chunks)} chunks for: '{question}'")
    for c in chunks:
        print(f"  [{c['chunk_id']}] score={c['score']}  {c['text'][:80]}...")

    return _generator.generate(question, chunks)


def answer(question: str):
    """Wk9-compatible: answer(question) -> (answer_str, chunks_list)"""
    result = ask(question)
    return result["answer"], result["sources"]


if __name__ == "__main__":
    test_questions = [
        "What is force?",
        "Explain Newton's second law in your own words.",
        "What is photosynthesis?",
    ]
    for q in test_questions:
        print(f"\n{'='*60}")
        print(f"Q: {q}")
        result = ask(q)
        print(f"A: {result['answer']}")
        print(f"   Sources: {result['chunk_ids']}")
