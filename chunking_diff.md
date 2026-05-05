# Chunking Diff — Wk9 vs Wk10

## What changed

**Wk9 chunker** (`src/chunking/chunker.py`):
- Word-count based sizing (chunk_size=300 words, overlap=50 words)
- No content-type detection — all text treated as one flat stream
- Sentence split with `re.split(r'(?<=[.!?])\s+', text)`
- No metadata attached to chunks
- Worked examples split mid-table (problem and solution in separate chunks)

**Wk10 chunker** (`src/chunking/chunker_v2.py`):
- Token-count based sizing with tiktoken cl100k_base (max 250 tokens, overlap 40 tokens)
- Content-type detection: `prose` / `worked_example` / `question_or_exercise`
- Worked examples kept as single chunks — never split mid-table
- Rich metadata per chunk: `chunk_id`, `content_type`, `source`, `chapter`, `token_count`
- LangChain `RecursiveCharacterTextSplitter` used for prose blocks

**Wk10 results:**
- Total chunks: **117** (prose: 107, worked_example: 8, question_or_exercise: 2)
- Average tokens per chunk: **123**
- Max tokens per chunk: **314**

---

## Sample chunks (3 specific examples from wk10_chunks.json)

**chunk_0000** — `prose` | 215 tokens
```
How Forces Affect MotionChapter 6
In Chapter 4, you learnt to describe the motion of an object in terms
of its position, velocity and acceleration. But you did not consider what
causes motion. Is t...
```

**chunk_0010** — `worked_example` | 165 tokens *(kept whole — problem + solution together)*
```
Example 6.1: Two forces of 10 N and 6 N are acting on a block lying on the
table as shown in Fig. 6.6. What is the magnitude and the direction of the net
force acting on the block in each case?
Fig. 6.6: Two forces acting on a block in three different manner
Answer:
(a) Net force = 10 N + 6 N = 16 N, acting towards the right side.
(b) Net force = 10 N − 6 N = 4 N
```

**chunk_0021** — `question_or_exercise` | 189 tokens
```
4. Holding the ends of the rubber band at A and B, place the stack of coins
near the middle of A and B. Now, using a finger of your other hand, push back
the stack of coins till the rubber band is pulled back to the mark C.
Then, release the stack of coins and observe its motion. Do you find that after
losing contact with the rubber band, the velocity of the stack of coins decreases...
```

---

## BM25 retrieval — Wk10 top-3 per question

| Question | Rank 1 | Rank 2 | Rank 3 | Content-type filter would help? |
|----------|--------|--------|--------|----------------------------------|
| What is force? | chunk_0068 prose (7.78) — "What is the net force acting on the toy car?" | chunk_0090 worked_example (4.70) — bullet/gun example | chunk_0022 question_or_exercise (4.52) — coins experiment | **Yes** — filtering to `prose` would remove exercise/worked_example chunks and promote the definition paragraph |
| State Newton's Second Law | chunk_0039 prose (14.73) — "6.5 Newton's Second Law of Motion" ✅ | chunk_0069 prose (10.14) — Third Law section | chunk_0030 prose (9.56) — inertia/Newton bio | No — top-1 is correct |
| What are the effects of force? | chunk_0090 worked_example (10.60) — bullet/gun example | chunk_0022 question_or_exercise (10.29) — coins experiment | chunk_0026 prose (9.92) — spring balance activity | **Yes** — top-1 and top-2 are a worked example and a question, not a prose definition |
| What is inertia? | chunk_0030 prose (4.77) — "Isaac Newton used the word inertia..." ✅ | chunk_0090 worked_example (4.70) — bullet/gun example | chunk_0022 question_or_exercise (4.52) — coins experiment | Partial — top-1 is correct but low score (4.77); ranks 2 and 3 are irrelevant |
| Why does passenger fall forward when bus stops? | chunk_0105 prose (12.22) — high jump landing mat | chunk_0060 prose (10.94) — airbag/collision chunk | chunk_0001 prose (10.87) — figure captions/Curiosity sidebar | **Yes** — all 3 are wrong; the inertia explanation (chunk_0031) was not retrieved at all |

---

## Observation

The Wk10 token-aware chunker correctly identifies and preserves all 8 worked examples as single chunks, directly fixing the teacher's complaint that the answer column was being ignored. chunk_0010 (Example 6.1) contains both the problem setup and the full solution in one retrieval unit — in Wk9, the solution "(a) Net force = 16 N" would have appeared in a separate chunk from the question, making it irretrievable.

The main remaining weakness is BM25 keyword matching on abstract queries. "What is force?" retrieves chunk_0068 (a toy-car exercise question containing the word "force") at rank 1 instead of the definition paragraph, because BM25 cannot distinguish between a question that uses the word "force" and the actual definition of force. Dense retrieval (Stage 2) resolves this: chunk_0002 scores 0.851 for the same query via semantic similarity, correctly identifying the definition context over the exercise chunk.
