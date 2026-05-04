# src/chunking/chunker_v2.py
# Week 10 — Stage 1 upgrade
#
# WHAT CHANGED FROM WK9:
#   - Content-type detection: prose / worked_example / question_or_exercise
#   - Token-aware sizing with tiktoken (not word count)
#   - Rich metadata per chunk: {chunk_id, source, section, content_type, page, token_count}
#   - Worked examples kept as a single chunk (not split mid-table)
#   - LangChain RecursiveCharacterTextSplitter used for prose chunks

import re
import json
import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict

# Cohort standard: 250 tokens max per chunk (spec §6 Stage 1)
MAX_TOKENS = 250
OVERLAP_TOKENS = 40

# tiktoken encoder — matches OpenAI text-embedding-3-small tokenisation
ENCODER = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(ENCODER.encode(text))


def detect_content_type(text: str) -> str:
    """
    Classify a block of text into one of three content types.
    Regex on heading and marker patterns.
    """
    lower = text.lower().strip()

    # Worked examples: 'Example X.X', 'Activity', 'Experiment', table rows (|)
    if re.match(r'^(example\s+\d|activity\s+\d|experiment\s+\d)', lower):
        return "worked_example"
    if "|" in text and lower.count("|") >= 4:       # table-like content
        return "worked_example"

    # Questions: end-of-chapter exercises, Q., In-text questions
    if re.match(r'^(exercise|in-text question|q\.\s*\d|questions\s*$)', lower):
        return "question_or_exercise"
    if re.match(r'^\d+[\.\)]\s+\w', lower):          # numbered question pattern
        return "question_or_exercise"

    return "prose"


def split_into_blocks(text: str) -> List[Dict]:
    """
    Split raw text into semantic blocks BEFORE applying token-size chunking.
    Worked examples are kept as single blocks — never split mid-example.
    Returns: list of {text, content_type}
    """
    # Split on double-newlines (paragraph boundaries) or section markers
    raw_blocks = re.split(r'\n{2,}', text)

    blocks = []
    current_example = []
    in_example = False

    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue

        ctype = detect_content_type(block)

        if ctype == "worked_example":
            # Absorb into current example buffer
            in_example = True
            current_example.append(block)

        else:
            # Flush buffered example first
            if current_example:
                blocks.append({
                    "text": "\n\n".join(current_example),
                    "content_type": "worked_example"
                })
                current_example = []
                in_example = False

            blocks.append({"text": block, "content_type": ctype})

    # Flush any remaining example
    if current_example:
        blocks.append({
            "text": "\n\n".join(current_example),
            "content_type": "worked_example"
        })

    return blocks


class ChunkerV2:
    def __init__(
        self,
        text: str,
        source: str = "iesc106.pdf",
        chapter: str = "Chapter 6 — How Forces Affect Motion",
        max_tokens: int = MAX_TOKENS,
        overlap_tokens: int = OVERLAP_TOKENS,
    ):
        self.text = text
        self.source = source
        self.chapter = chapter
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens

        # LangChain splitter for prose blocks only
        # ~4 chars per token is a reasonable approximation for English text
        self.prose_splitter = RecursiveCharacterTextSplitter(
            chunk_size=max_tokens * 4,
            chunk_overlap=overlap_tokens * 4,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )

    def create_chunks(self) -> List[Dict]:
        """
        Returns a list of chunk dicts with full metadata.
        Each dict: {chunk_id, text, content_type, source, chapter, token_count}
        """
        blocks = split_into_blocks(self.text)
        chunks = []
        chunk_id = 0

        for block in blocks:
            btext = block["text"]
            ctype = block["content_type"]
            tokens = count_tokens(btext)

            if ctype == "worked_example":
                # Keep the entire example as ONE chunk, even if over limit
                # (splitting a worked example mid-table is the bug we're fixing)
                chunks.append({
                    "chunk_id": f"chunk_{chunk_id:04d}",
                    "text": btext,
                    "content_type": ctype,
                    "source": self.source,
                    "chapter": self.chapter,
                    "token_count": tokens,
                })
                chunk_id += 1

            elif tokens <= self.max_tokens:
                # Small prose block — keep as one chunk
                chunks.append({
                    "chunk_id": f"chunk_{chunk_id:04d}",
                    "text": btext,
                    "content_type": ctype,
                    "source": self.source,
                    "chapter": self.chapter,
                    "token_count": tokens,
                })
                chunk_id += 1

            else:
                # Large prose block — split with RecursiveCharacterTextSplitter
                sub_texts = self.prose_splitter.split_text(btext)
                for sub in sub_texts:
                    if not sub.strip():
                        continue
                    chunks.append({
                        "chunk_id": f"chunk_{chunk_id:04d}",
                        "text": sub.strip(),
                        "content_type": ctype,
                        "source": self.source,
                        "chapter": self.chapter,
                        "token_count": count_tokens(sub),
                    })
                    chunk_id += 1

        return chunks

    def save_json(self, chunks: List[Dict], path: str = "wk10_chunks.json"):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(chunks)} chunks to {path}")


if __name__ == "__main__":
    import os
    processed_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "Data", "Processed", "cleaned.txt"
    )
    with open(processed_path, "r", encoding="utf-8") as f:
        text = f.read()

    chunker = ChunkerV2(text)
    chunks = chunker.create_chunks()

    # Summary
    by_type = {}
    for c in chunks:
        by_type[c["content_type"]] = by_type.get(c["content_type"], 0) + 1

    print(f"Total chunks  : {len(chunks)}")
    print(f"By type       : {by_type}")
    print(f"Avg tokens    : {sum(c['token_count'] for c in chunks) // len(chunks)}")
    print(f"Max tokens    : {max(c['token_count'] for c in chunks)}")
    print("\nSample prose chunk:")
    prose = [c for c in chunks if c["content_type"] == "prose"]
    if prose:
        print(json.dumps(prose[0], indent=2))
    print("\nSample worked_example chunk:")
    ex = [c for c in chunks if c["content_type"] == "worked_example"]
    if ex:
        print(json.dumps(ex[0], indent=2))

    chunker.save_json(chunks, "wk10_chunks.json")
