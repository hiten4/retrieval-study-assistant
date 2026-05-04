# src/generation/llm_v2.py
# Week 10 — Stage 3
# LLM: Groq (llama-3.3-70b-versatile) — free, fast, no Anthropic key needed
# Returns {answer, sources, chunk_ids}
# temperature=0 for reproducible evaluation

import os
from groq import Groq
from dotenv import load_dotenv

try:
    from langchain_core.prompts import PromptTemplate   # langchain >= 0.2
except ImportError:
    from langchain.prompts import PromptTemplate        # langchain < 0.2

# load_dotenv() must be called with the explicit path when running from a
# subdirectory — this finds .env even when imported from src/generation/
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

# ── Prompt v1 — PERMISSIVE (for Stage 3 before/after comparison) ─────────────
PROMPT_V1 = PromptTemplate(
    input_variables=["context", "question"],
    template="""Answer the question using the context below.

Context:
{context}

Question:
{question}

Answer:""",
)

# ── Prompt v2 — STRICT (refusal + chunk_id citations) ────────────────────────
PROMPT_V2 = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are a NCERT Class 9 Science study assistant for PariShiksha.

STRICT RULES — follow every one:
1. Read the context carefully. Every factual claim in your answer MUST come from the context.
2. After every factual claim, cite the source chunk in square brackets: [Source: chunk_id].
3. If the answer to the question is NOT present in the context, reply with exactly:
   "I don't have that in my study materials."
   Do not add anything else.
4. Do NOT use any external knowledge. Do NOT guess.
5. Keep answers concise — 2 to 4 sentences maximum.

Context (with chunk IDs):
{context}

Question:
{question}

Answer:""",
)


def format_context_with_ids(chunks: list) -> str:
    parts = []
    for c in chunks:
        cid  = c.get("chunk_id", "unknown")
        text = c.get("text", "")
        parts.append(f"[{cid}]\n{text}")
    return "\n\n---\n\n".join(parts)


class LLMGeneratorV2:
    def __init__(
        self,
        model_name: str = "llama-3.3-70b-versatile",   # free Groq model
        prompt_version: str = "v2",
        temperature: float = 0,
    ):
        self.model_name    = model_name
        self.prompt        = PROMPT_V2 if prompt_version == "v2" else PROMPT_V1
        self.prompt_version = prompt_version
        self.temperature   = temperature

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found.\n"
                "1. Get a free key at https://console.groq.com\n"
                "2. Add to your .env file:  GROQ_API_KEY=gsk_xxxx"
            )
        self.client = Groq(api_key=api_key)

    def generate(self, question: str, chunks: list) -> dict:
        """
        Generate a grounded answer.
        Returns: {answer, sources, chunk_ids}
        """
        context     = format_context_with_ids(chunks)
        prompt_text = self.prompt.format(context=context, question=question)

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt_text}],
            temperature=self.temperature,
        )
        answer_text = response.choices[0].message.content.strip()

        return {
            "answer":    answer_text,
            "sources":   [c["text"] for c in chunks],
            "chunk_ids": [c["chunk_id"] for c in chunks],
        }

    def generate_plain(self, question: str, context: str) -> str:
        """Backward-compatible interface for the evaluation judge."""
        prompt_text = self.prompt.format(context=context, question=question)
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt_text}],
            temperature=self.temperature,
        )
        return response.choices[0].message.content.strip()


if __name__ == "__main__":
    gen_v1 = LLMGeneratorV2(prompt_version="v1")
    gen_v2 = LLMGeneratorV2(prompt_version="v2")

    dummy_chunks = [{
        "chunk_id": "chunk_0001",
        "text": "Force is a physical quantity with both magnitude and direction, measured in Newtons.",
        "score": 0.95,
    }]

    print("=== PERMISSIVE v1 ===")
    print(gen_v1.generate("What is force?", dummy_chunks)["answer"])

    print("\n=== STRICT v2 ===")
    print(gen_v2.generate("What is photosynthesis?", dummy_chunks)["answer"])
