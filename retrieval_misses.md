# Retrieval Misses — Stage 2

Top-1 dense retrieval was wrong for the following queries.
Each miss is diagnosed into one of: chunking miss / embedding limitation / bad ranking.

---

## Miss 1

**Query**: Why does a passenger fall forward when a moving bus stops suddenly?

**Top-1 chunk_id**: `chunk_0060` (similarity score: 0.8016)

**Top-1 chunk text (first 250 chars)**:
```
For a similar reason, airbags are provided in vehicles
(Fig. 6.19). In the event of a collision and the vehicle coming to an abrupt halt,
the airbag inflates rapidly and cushions the impact on the passengers...
```

**Diagnosis**: Bad ranking

The query asks about **inertia** — why a passenger (a body at rest relative to the bus) continues moving forward when the bus decelerates suddenly. The correct explanation is in chunk_0031 ("if the net force acting on an object is zero, the body cannot begin to move or change its velocity"), which ranked 3rd at score 0.7697. chunk_0060 ranked top-1 at 0.8016 because it also describes a vehicle stopping abruptly and passenger safety — the embedding model found this semantically closer to the query than the actual inertia explanation. The query and chunk_0060 share the concepts "vehicle stops" + "passenger impact," but the mechanism being asked about (inertia, Newton's First Law) is different from the mechanism described (airbag cushioning, Newton's Third Law).

---

## Miss 2

**Query**: What is action and reaction?

**Top-1 chunk_id**: `chunk_0069` (similarity score: 0.7971)

**Top-1 chunk text (first 250 chars)**:
```
How Forces Affect Motion107
6.6 Newton's Third Law of Motion
We have described the behaviour of an object when a net
force acts on it. But do you remember...
```

**Diagnosis**: Chunking miss

chunk_0069 is the section heading chunk for Newton's Third Law, which introduces the section but does not yet state the action-reaction pairs clearly. The explicit action-reaction statement ("whenever one object exerts a force on a second object, the second object simultaneously exerts a force equal in magnitude and opposite in direction") is in chunk_0077, which ranked lower (score not in top-1 for this specific query). The section heading chunk scored highest because it contains "Newton's Third Law of Motion" — the closest phrase to "action and reaction" — but the actual definition is one chunk further. This is a chunk boundary issue: the introductory heading and the definitive statement were split across two chunks, so retrieval returns the introduction rather than the answer.

---

## Miss 3

**Query**: Why does a body resist change in motion?

**Top-1 chunk_id**: `chunk_0016` (similarity score: not top for relevant content)

**Top-1 chunk text (first 250 chars)**:
```
[chunk_0016 — irrelevant PDF extraction content; model correctly refused]
```

**Diagnosis**: Embedding limitation

This is a paraphrase of "What is inertia?" but uses completely different vocabulary — "resist change in motion" rather than "inertia." The correct chunk is chunk_0030: "Isaac Newton used the word inertia to describe the tendency of objects to resist change in their state of rest or uniform motion." Although chunk_0030 contains the phrase "resist change in their state" which semantically matches the query, the embedding model failed to bridge the paraphrase gap and ranked irrelevant chunks higher. As a result the LLM correctly refused with "I don't have that in my study materials" — the right refusal behaviour, but for the wrong reason (retrieval miss rather than genuine absence). This query would benefit from MultiQuery or HyDE: generating a variant like "what is inertia?" would retrieve chunk_0030 correctly.

---

## Pattern

All 3 misses share a common root: the correct chunk **exists in the collection** but is not ranked top-1. Miss 1 is a ranking error where a semantically adjacent chunk about a related but different mechanism outranks the correct explanation. Miss 2 is a chunk boundary issue where the section heading ranks above the actual definition. Miss 3 is a paraphrase gap where the query vocabulary differs enough from the chunk vocabulary that the embedding model cannot bridge them. None of the misses are caused by the answer being absent from the corpus — they are all retrieval failures, not corpus failures.
