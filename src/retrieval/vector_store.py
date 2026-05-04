import os
import json
import time
from typing import List, Dict

import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

# ── Constants ──────────────────────────────────────────────────────────────
# Running locally via sentence-transformers — no API token needed
EMBEDDING_MODEL = "mixedbread-ai/mxbai-embed-large-v1"
CHROMA_PATH     = "./chroma_wk10_hf"
COLLECTION_NAME = "ncert_ch6_hf"
CHUNKS_PATH     = "wk10_chunks.json"


class VectorStore:
    def __init__(
        self,
        chroma_path: str = CHROMA_PATH,
        collection_name: str = COLLECTION_NAME,
        embedding_model: str = EMBEDDING_MODEL,
    ):
        # ── Use SentenceTransformerEmbeddingFunction (runs 100% locally) ──
        # This downloads the model once (~500MB) then caches it.
        # No HF_TOKEN needed. No API calls. No JSON parse errors.
        self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )

        self.client = chromadb.PersistentClient(path=chroma_path)

        # Same model used at index-time AND query-time — locked here
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.ef,
            metadata={"hnsw:space": "cosine"},
        )

    def load_and_embed(self, chunks_path: str = CHUNKS_PATH, force: bool = False):
        existing = self.collection.count()
        if existing > 0 and not force:
            print(f"Collection has {existing} chunks — skipping embedding.")
            print("(Pass force=True to re-embed from scratch)")
            return

        with open(chunks_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        print(f"Embedding {len(chunks)} chunks locally with {EMBEDDING_MODEL}...")
        print("(First run downloads the model ~500MB — subsequent runs are instant)")

        start = time.time()

        # Smaller batch size for local CPU — avoids memory spikes
        batch_size = 32
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i: i + batch_size]
            self.collection.add(
                ids=[c["chunk_id"] for c in batch],
                documents=[c["text"] for c in batch],
                metadatas=[{
                    "content_type": c["content_type"],
                    "source":       c["source"],
                    "chapter":      c.get("chapter", ""),
                    "token_count":  c.get("token_count", 0),
                } for c in batch],
            )
            print(f"  Embedded batch {i // batch_size + 1} / {(len(chunks) - 1) // batch_size + 1}")

        elapsed = time.time() - start
        print(f"Done in {elapsed:.1f}s. Total chunks indexed: {self.collection.count()}")

    def retrieve(self, query: str, k: int = 5) -> List[Dict]:
        """
        Dense retrieval — returns top-k chunks with similarity scores.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )

        chunks = []
        for i in range(len(results["ids"][0])):
            # Chroma returns cosine distance (0=identical, 2=opposite)
            # Convert to similarity: 1 - distance/2
            distance   = results["distances"][0][i]
            similarity = round(1 - distance / 2, 4)

            chunks.append({
                "chunk_id":     results["ids"][0][i],
                "text":         results["documents"][0][i],
                "content_type": results["metadatas"][0][i].get("content_type", "prose"),
                "score":        similarity,
            })

        return chunks

    def retrieve_with_filter(
        self,
        query: str,
        k: int = 5,
        content_type: str = None,
    ) -> List[Dict]:
        """
        Dense retrieval with optional content_type metadata filter.
        """
        where = {"content_type": content_type} if content_type else None

        results = self.collection.query(
            query_texts=[query],
            n_results=k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        chunks = []
        for i in range(len(results["ids"][0])):
            distance   = results["distances"][0][i]
            similarity = round(1 - distance / 2, 4)
            chunks.append({
                "chunk_id":     results["ids"][0][i],
                "text":         results["documents"][0][i],
                "content_type": results["metadatas"][0][i].get("content_type", "prose"),
                "score":        similarity,
            })

        return chunks


if __name__ == "__main__":
    store = VectorStore()
    store.load_and_embed()

    test_q = "What is Newton's Second Law of Motion?"
    results = store.retrieve(test_q, k=5)

    print(f"\nQuery: {test_q}")
    for r in results:
        print(f"  [{r['chunk_id']}] score={r['score']}  type={r['content_type']}")
        print(f"    {r['text'][:120]}...")
