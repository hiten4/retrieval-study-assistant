# Prompt Diff — v1 (Permissive) vs v2 (Strict)

## Prompt v1 — Permissive

```
Answer the question using the context below.

Context:
{context}

Question:
{question}

Answer:
```

## Prompt v2 — Strict

```
You are a NCERT Class 9 Science study assistant for PariShiksha.

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

Answer:
```

---

## Comparison on 3 queries

### Query 1 — In-scope: "What is force?"

**v1 answer:**
```
Force is a physical quantity for which we need to specify direction along with its
magnitude. It can set an object in motion, bring it to rest, or change its velocity,
producing acceleration.
```

**v2 answer:**
```
Force is a physical quantity for which we need to specify direction along with its
magnitude [Source: chunk_0002].
```

**Observation:** Both answers are factually correct. v1 added "producing acceleration" which is not directly stated in the retrieved chunks chunk_0002, chunk_0039, chunk_0049 — a small case of the model extending beyond context. v2 stays strictly within what the chunk states and cites the source, making grounding verifiable. v2 is shorter but every word is traceable.

---

### Query 2 — Paraphrased: "Explain Newton's second law in your own words."

**v1 answer:**
```
Newton's second law states that when a force acts on an object, it causes the object
to accelerate, or change its velocity, in the direction of the force. The amount of
acceleration depends on the strength of the force and the mass of the object. In other
words, the more force applied to an object, the more it will accelerate, and the heavier
the object is, the less it will accelerate. This law can also be expressed in terms of
momentum, which is the product of an object's mass and velocity, and it states that the
rate of change of momentum is proportional to the net force acting on the object.
```

**v2 answer:**
```
Newton's second law states that the rate of change of momentum of an object is
proportional to the net force and takes place in the direction in which the net force
acts [Source: chunk_0056]. It can also be stated as when a net force acts on an object,
the object accelerates in the direction of the net force [Source: chunk_0049]. The
magnitude of the acceleration is proportional to the magnitude of the net force and is
inversely proportional to the mass of the object [Source: chunk_0049].
```

**Observation:** v1 produced a longer conversational answer ("in other words, the more force applied...") paraphrasing beyond the retrieved context chunks_0056, chunk_0049, chunk_0036. The phrasing "the heavier the object is, the less it will accelerate" is a correct inference but is not a verbatim statement from the chunks. v2 cites both the momentum form (chunk_0056) and the F=ma form (chunk_0049) explicitly, keeping strictly to what was retrieved. The teacher's requirement — "which paragraph did this come from?" — is directly satisfied by v2.

---

### Query 3 — Out-of-scope: "What is photosynthesis?"

**v1 answer:**
```
The context provided does not mention photosynthesis. The text discusses Newton's laws
of motion, specifically the second and third laws, and provides examples of how they
apply to everyday situations, such as a balloon expelling air and a person climbing a
tree. There is no mention of photosynthesis, which is the process by which plants and
some other organisms convert light energy into chemical energy.
```

**v2 answer:**
```
I don't have that in my study materials.
```

**Observation:** This is the most important difference between the two prompts. v1 correctly identified that photosynthesis was absent from the context — then immediately defined photosynthesis from parametric memory anyway. A student reading v1's answer receives a correct explanation of photosynthesis, creating the impression that the PariShiksha assistant covers Biology. v2 refused cleanly with the exact required phrase and added nothing. The strict "reply with exactly... Do not add anything else" instruction eliminated the verbose non-refusal that v1 produced.

---

## Conclusion

The single observation that forced the revision from v1 to v2 was the photosynthesis response. v1 said "the context does not mention photosynthesis" and then explained what photosynthesis is — demonstrating that "answer using the context" is interpreted as "prefer the context but supplement from memory when the topic is absent." This is a product safety failure: a student asking about photosynthesis would receive a confident, accurate answer, falsely expanding the perceived scope of the assistant. Switching to the constraint phrasing — "reply with exactly: 'I don't have that in my study materials.' Do not add anything else." — eliminated this behaviour completely on all 3 out-of-scope test queries.
