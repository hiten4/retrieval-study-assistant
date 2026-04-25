import os
from src.extraction.pdf_loader import PDFLoader
from src.extraction.clean_text import TextCleaner
from src.chunking.chunker import Chunker
from src.retrieval.bm25 import BM25Retriever
from src.generation.llm import LLMGenerator


# ── Path: resolve relative to this file so it works on any machine ──────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(BASE_DIR, "Data", "Raw", "iesc106.pdf")

# ── Load ─────────────────────────────────────────────────────────────────────
loader = PDFLoader(PDF_PATH)
raw_text = loader.load()

# ── Clean ────────────────────────────────────────────────────────────────────
cleaner = TextCleaner(raw_text)
cleaned_text = cleaner.clean()

# ── Chunk ────────────────────────────────────────────────────────────────────
chunker = Chunker(cleaned_text, chunk_size=300, overlap=50)
chunks = chunker.create_chunks()

# ── Retriever + Generator ────────────────────────────────────────────────────
retriever = BM25Retriever(chunks)
generator = LLMGenerator(model_name="phi3")


def answer(question: str):
    retrieved = retriever.retrieve(question, top_k=3)   # fixed: was .search()
    context = "\n\n".join(retrieved)
    ans = generator.generate(question, context)          # fixed: was generate_answer()
    return ans, retrieved


#── Test ─────────────────────────────────────────────────────────────────────
# if __name__ == "__main__":
#     q = "What is Force?"
#     ans, ctx = answer(q)

#     print("Answer:", ans)
#     print("\n--- Retrieved Chunks ---")
#     for i, chunk in enumerate(ctx, 1):
#         print(f"\n[{i}] {chunk[:200]}...")

# if __name__ == "__main__":
#     while True:
#         q = input("\nAsk (or type 'exit'): ")
#         if q.lower() == "exit":
#             break

#         ans, ctx = answer(q)
#         print("\nAnswer:", ans)