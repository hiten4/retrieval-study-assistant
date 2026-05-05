# Fix Memo — Stage 5

## The single worst failure from Stage 4 eval

**Question**: Why does a body resist change in motion?

**System answer**:
```
I don't have that in my study materials.
```

**Top-3 retrieved chunk_ids**: `chunk_0016`, `chunk_0037`, `chunk_0000`, `chunk_0059`, `chunk_0031`

**Why this is the worst failure**: This is a paraphrased question about inertia. The correct answer exists in the corpus — chunk_0031 contains "if the net force acting on an object is zero, the body cannot begin to move or change its velocity" and chunk_0030 contains "Isaac Newton used the word inertia to describe the tendency of objects to resist change in their state of rest or uniform motion." Both correct chunks were retrieved (chunk_0031 at position 5), but the top-ranked chunks (chunk_0016, chunk_0037, chunk_0000) were irrelevant PDF noise, so the LLM correctly refused. The answer existed in context but was buried below the noise chunks.

---

## Failure mode diagnosis (§3 catalog)

**Category**: Synonym / paraphrase mismatch

The query uses "resist change in motion" while the corpus uses "inertia" and "tendency of objects to resist change in their state of rest or uniform motion." The embedding model partially bridged this gap (chunk_0031 appeared at rank 5) but ranked PDF noise chunks higher. This is a retrieval ranking failure caused by paraphrase vocabulary gap combined with corpus noise diluting the relevant signal.

---

## The one targeted fix

**Fix chosen**: Metadata filter — retrieve only `prose` content_type chunks, excluding PDF noise chunks that are typed as `prose` but contain figure captions and sidebar content.

**Why this fix matches the diagnosis**: The top-ranked irrelevant chunks (chunk_0016, chunk_0037, chunk_0000) all contain figure caption text and chapter header artifacts from PDF extraction. If we filter retrieval to only return chunks where the text does not begin with "Fig." or "Chapter", the noise chunks drop out and chunk_0031 / chunk_0030 rise to top-3, giving the LLM the correct context.

**Implementation**: In `main_v2.py`, `ask()` function — add a post-retrieval filter:

```python
# After: chunks = _store.retrieve(question, k=7)
# Add:
chunks = [c for c in chunks if not c["text"].strip().startswith(("Fig.", "Chapter", "Grade"))][:5]
```

This increases k to 7 to compensate for filtered-out noise chunks, then trims back to 5 clean chunks.

---

## Before/after delta

| Metric | Before (eval_scored.csv) | After (eval_v2_scored.csv) | Delta |
|--------|--------------------------|---------------------------|-------|
| Correct (yes) | 8 / 12 (67%) | 9 / 12 (75%) | +1 |
| Grounded | 8 / 12 (67%) | 9 / 12 (75%) | +1 |
| OOS Refused | 3 / 3 (100%) | 3 / 3 (100%) | 0 |

**On the targeted question ("Why does a body resist change in motion?"):**
- Before: correctness=no, grounded=no (model refused because noise chunks were top-ranked)
- After: correctness=yes, grounded=yes (chunk_0030 now in top-3, model answers from inertia definition)

---

## Honest assessment

The fix worked specifically on the targeted question — removing figure-caption and chapter-header noise from the top-k results allowed chunk_0030 (the inertia definition) to surface in the LLM's context window. The overall correctness improved by 1 question (8→9 out of 12).

The fix did not affect the OOS refusal rate (already 3/3 — 100%) and did not hurt any previously correct answers. However it is a brittle fix: it relies on noise chunks predictably starting with "Fig." or "Grade", which is true for this chapter but may not generalise to other chapters where body text also starts with these prefixes.

The more principled fix would be to improve PDF extraction to separate figure captions from body paragraphs at ingestion time (using OpenDataLoader-PDF's structured JSON output with element types), rather than filtering at retrieval time. That is the Wk11 priority.
