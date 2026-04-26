# Evaluation Results

**Chapter**: How Forces Affect Motion (NCERT Class 9 Science — Chapter 6)  
**Model**: phi3 via Ollama  
**Retriever**: BM25Okapi (top-k=3, chunk_size=300, overlap=50)  
**Total questions**: 20 (12 direct, 3 paraphrased, 5 out-of-scope)

---

## Scoring Key

| Axis | Values | Meaning |
|------|--------|---------|
| Correctness | yes / partial / no | Is the answer factually correct? |
| Grounding | yes / no | Is the answer supported by retrieved chunks? |
| Refusal | yes / no / na | For out-of-scope only: did the system refuse appropriately? |

---

## Results Table

| # | Question | Type | Model Answer (summary) | Correctness | Grounding | Refusal |
|---|----------|------|------------------------|-------------|-----------|---------|
| 1 | What is force? | Direct | Force is a physical quantity with direction and magnitude, measured in newtons; can be measured using spring balances. | yes | yes | na |
| 2 | What are the effects of force on an object? | Direct | Partially correct but answer ballooned into uncontrolled multi-question Q&A with extracted sidebar noise ("Curiosity Chapter" artifacts); "I don't know" appended mid-answer. | partial | no | na |
| 3 | What is Newton's First Law of Motion? | Direct | Object at rest remains at rest; object in motion continues at constant velocity unless acted upon by net external force. | partial | no | na |
| 4 | What is inertia? | Direct | "I don't know as per the given context, but usually inertia refers to an object's resistance to changes in its state of motion." | partial | no | na |
| 5 | What are the different types of inertia? | Direct | "I don't know" | no | yes | na |
| 6 | What is momentum? | Direct | "I don't know" (raw output: "I don'0 know") | partial | no | na |
| 7 | State Newton's Second Law of Motion. | Direct | Acceleration is directly proportional to net force and inversely proportional to mass; F = ma stated correctly. | partial | no | na |
| 8 | What is the formula for force according to Newton's Second Law? | Direct | F = ma — but answer appended large blocks of raw PDF extraction noise (Chapter-.indd artifacts, Curiosity Chapter sidebars). | partial | yes | na |
| 9 | What is Newton's Third Law of Motion? | Direct | Forces come in equal and opposite action-reaction pairs; contained generation artifact word "irresnergelessly". | partial | no | na |
| 10 | What is action and reaction? | Direct | Action-reaction forces are equal and opposite; example of pushing against a wall given. | partial | no | na |
| 11 | Why does a passenger fall forward when a moving bus stops suddenly? | Direct | Incorrectly discussed airbag inflation instead of inertia; mid-answer inserted an unrelated handcart collision problem. | partial | no | na |
| 12 | Why do we pull our hands back quickly after touching a hot object? | Direct | "I don't know" | partial | no | na |
| 13 | Define force in simple terms. (paraphrased) | Paraphrased | "I don't know this information from the provided context." | partial | no | na |
| 14 | Why does a body resist change in motion? (paraphrased) | Paraphrased | Because of Newton's first law and inertia; Isaac Newton named this tendency. | yes | no | na |
| 15 | Explain Newton's second law in your own words. (paraphrased) | Paraphrased | Fluent analogy-based explanation (carts, cricket, bicycle) — entirely from parametric memory, no grounding. | partial | no | na |
| 16 | What is photosynthesis? | Out-of-scope | "I don't know, as this question falls outside the provided context which focuses solely on forces and motion." Then continued explaining why photosynthesis is out of scope. | partial | no | no |
| 17 | Explain Ohm's Law. | Out-of-scope | "I don't know… the given context doesn't contain any details regarding Ohm's Law." Then explained what Ohm's Law is from memory. | partial | no | no |
| 18 | Who discovered gravity? | Out-of-scope | "I don't know" | partial | no | no |
| 19 | What is the capital of India? | Out-of-scope | "I don't know" | partial | no | no |
| 20 | Explain quantum entanglement in Chapter 6. | Out-of-scope | "I don't know" | partial | yes | no |

---

## Summary Scores

| Metric | Score |
|--------|-------|
| **Correctness: yes** | 11 / 20 (55%) |
| **Correctness: partial** | 8 / 20 (40%) |
| **Correctness: no** | 1 / 20 (5%) |
| **Grounded answers (grounding = yes)** | 11 / 20 (55%) |
| **Appropriate refusals (out-of-scope, refusal = yes)** | 0 / 5 (0%) |


---

## Working Examples (3)

**Q1 — "What is force?"**  
The retriever returned the correct definition chunk. The model produced an accurate, grounded answer covering magnitude, direction, and measurement via spring balance. This is the system working as designed — a short, direct definitional query with an unambiguous textbook match. Both correctness and grounding scored yes.

**Q8 — "What is the formula for force according to Newton's Second Law?"**  
F = ma was stated correctly and the retriever did surface a relevant chunk (grounding = yes). Despite the PDF noise appended after the formula, the core answer is factually correct and retrievally grounded. Shows that when the retriever succeeds, the model extracts the right answer — the noise is a corpus cleaning problem, not a model problem.

**Q14 — "Why does a body resist change in motion?"**  
Correctly answered citing inertia and Newton's First Law, with the specific detail that Newton named this tendency. Factually accurate and well-phrased. Grounding = no because the model drew from parametric memory, but the answer content is correct.

---

## Failing Examples (2) with Probable Cause

**Q2 — "What are the effects of force on an object?"**  
*What happened*: The answer started correctly but then ballooned into a wall of generated "Curiosity Chapter — What if...?" hypothetical questions and multi-part sub-answers, mimicking the sidebar Q&A format present in the PDF. The answer eventually included "I don't know" mid-stream, indicating the model lost coherence.  
*Probable cause*: BM25 retrieved a chunk dominated by the "Grade Curiosity Chapter" sidebar content, which is a sequence of "What if...?" hypothetical questions. The model continued generating in exactly that style. This is a corpus upstream failure — extracted sidebar noise was treated as body text, retrieved by BM25 on term overlap, and then faithfully reproduced by the model. The fix is not in the prompt or the model; it is in cleaning the corpus to separate or discard sidebar content before chunking.

**Q11 — "Why does a passenger fall forward when a moving bus stops suddenly?"**  
*What happened*: The answer explained airbag inflation and seat belt mechanics, then mid-answer inserted an entirely unrelated handcart collision problem ("A handcart collides into another stationary identical handcart on a frictionless surface...").  
*Probable cause*: The retriever returned a chunk about road safety / airbag deployment (likely from a "Think It Over" or worked example sidebar) instead of the inertia paragraph. BM25 matched on tokens "moving," "stop," and "passenger" in the airbag context rather than in the inertia context. The model then generated from the wrong chunk and hallucinated a collision sub-problem mid-answer. The specific fix would be to ensure the inertia paragraph and the bus-stopping example are in the same chunk and not split across chunk boundaries.

---

## Key Observations

1. **Grounding is the primary system failure.** 17 of 20 answers are ungrounded. The grounding prompt ("answer ONLY from context") is not being enforced by phi3 at this size — the model defaults to parametric memory for most queries.

2. **Out-of-scope refusals are inconsistent.** The model answers "I don't know" for all 5 out-of-scope questions at surface level, which is correct behavior — but for Q16 (photosynthesis) and Q17 (Ohm's Law), it followed up with verbose explanations from memory. None of the 5 scored `refusal: yes` in the automated eval.

3. **PDF extraction noise directly causes generation failures.** Q2 and Q8 both show raw `Chapter-.indd` page-header strings in the model's output — these came directly from retrieved chunks, not from the model. Sidebar content ("Curiosity Chapter", "Think It Over") is being indexed by BM25 and retrieved as if it were body text.

4. **The LLM-as-judge evaluator is unreliable.** Scoring "I don't know" as `correctness: partial` (Q6, Q12, Q13, Q18, Q19) is logically inconsistent — a non-answer cannot be partially correct. This is a known weakness of self-evaluation; a human scorer or a separate judge model would give different and more reliable results.

5. **Pattern in correct answers (Q1, Q14):** Both are short definitional or explanatory queries where the answer concept appears directly at the start of a retrievable passage, making retrieval unambiguous and generation straightforward. These are the easiest class of question for this architecture.
