# Reflection Questionnaire — Week 9 Mini-Project
**Student**: Hiten  
**Project**: Retrieval-Ready Study Assistant for NCERT Science  
**Chapter used**: How Forces Affect Motion (NCERT Class 9 Science)

---

## Part A — Implementation Artifacts

### A1. Chunking Parameters

**Parameters settled on:**
- `chunk_size = 300` (word count)
- `overlap = 50` (word count, carried forward from previous chunk's tail)
- Method: sentence-aware split using `re.split(r'(?<=[.!?])\s+', text)` before applying the word-count window

**What pushed me to these values:**

I initially set `chunk_size = 200` (visible in the git history at commit `a45014f`). When I ran the first retrieval tests on Chapter 6, I noticed the retriever was returning chunks that ended mid-explanation — specifically, a chunk would contain the setup of a worked example ("Consider a car moving at...") but the solution was cut into the next chunk. Queries about those examples would retrieve the problem statement but not the answer, and the LLM would then either say "I don't know" or generate a fabricated solution. Increasing to 300 words kept most problem-solution pairs together. I set overlap at 50 words because the sentence-split boundaries sometimes left transitional sentences (like "From the above experiment we can conclude...") stranded at the start of a new chunk with no context — the overlap carries the tail of the previous reasoning into the next chunk, which helps BM25 score transition sentences correctly.

I did not test 500-word chunks because Chapter 6 sections are themselves only 200–400 words long; a 500-word chunk would merge multiple concepts (e.g., First Law and Second Law) into one retrieval unit, which I expected would dilute BM25 scores for specific law queries.

---

### A2. A Retrieved Chunk That Was Wrong for Its Query

**Query**: "What are the effects of force on an object?"

**Wrong chunk retrieved** (paraphrased from actual output):
> "Chapter-.indd -103Chapter-.indd -- ::-- :: Exploration|Grade . Newton's Second Law of Motion You know that a force can set an object in motion, bring it to rest, or change its velocity. A change in velocity means that the object is accelerating. Thus, we seek relationship between net force acting on an object and acceleration... Chapter-.indd -104..."

**Why the retriever returned it:**

The chunk contains the phrase "effects... force on an object" implicitly — it mentions force setting objects in motion, bringing them to rest, changing velocity — all of which are effects of force. BM25 matched on the individual tokens "force," "object," "motion," and "velocity," which overlap heavily with the query. The problem is that this chunk is a PDF extraction artifact: it contains page-header strings ("Chapter-.indd -- ::--") mixed into the body text, and the actual explanation of effects is fragmented across what should have been a clean paragraph. BM25 has no way to know the chunk is structurally broken — it just sees high term overlap and returns it. The retriever did not fail; the corpus did.

---

### A3. Grounding Prompt — v1 and Final

**Version 1 (initial):**
```
You are a NCERT study assistant.

STRICT RULES:
- Answer ONLY from the provided context
- If answer is not in context, say "I don't know"
- Do NOT add external knowledge

Context:
{context}

Question:
{question}
```

**Final version** (same as v1 — I did not iterate on the prompt during this build):

I wrote one version of the grounding prompt and did not change it. Honestly, I was focused on getting the retrieval and evaluation pipeline running and did not run the kind of single-variable prompt experiments the expert hints recommend. Looking at my evaluation results, this was a mistake. The prompt uses "Answer ONLY from the provided context" — which the expert hints specifically identify as the permissive phrasing that LLMs interpret as "prefer the context." The results bear this out: phi3 answered Newton's Second Law, Newton's Third Law, and inertia from parametric memory without any grounding, even though the prompt says ONLY. Had I tested both phrasings — "answer only from context" vs. "if the answer is not present word-for-word in the context below, respond with 'I cannot answer this from the textbook'" — I would likely have seen a measurable difference in grounding scores.

The specific failure that should have triggered a prompt revision was Q15 ("Explain Newton's second law in your own words"), where the model produced a fluent, detailed, entirely memory-generated answer with no connection to retrieved chunks whatsoever. That was the moment I should have changed the prompt. I did not catch it until running the full evaluation.

---

## Part B — Numbers from Evaluation

### B1. Evaluation Scores

Out of 20 questions:
- **(a) Correct** (correctness = yes): **3 / 20**
- **(b) Grounded** (answer supported by retrieved chunks): **3 / 20**
- **(c) Appropriate refusals** (out-of-scope questions, refusal = yes): **0 / 5**

The number that bothers me most is the refusal score: **0 out of 5**. A grounding failure in a factual question is a quality problem. A refusal failure on an out-of-scope question is a trust problem — in the PariShiksha context, a parent whose daughter received a confident answer about quantum entanglement from a system that was only supposed to cover How Forces Affect Motion would not just be unhappy with quality; they would lose trust in the product entirely. The grounding score is bad engineering. The refusal score is a product safety failure.

### B2. Chunk-Size Experiment

I did not run a controlled chunk-size comparison as part of the Stretch tier. I changed the chunk size once (from 200 to 300, commit `a45014f`) based on observing retrieval output, but I did not record scores at chunk_size=200 to create a measurable before/after delta. If I had two more days, this would be the first experiment I would run.

### B3. Model Family Comparison

I did not compare model families in this submission. The full system runs on phi3 via Ollama only. I was aware the spec asked for a T5 or extractive QA comparison, but integrating a second model family while also fixing retrieval and evaluation bugs was more than I could complete in the time available. If I were to run this comparison, I would choose phi3 (decoder-only, current build) vs. `deepset/roberta-base-squad2` (extractive QA), because extractive QA cannot hallucinate by definition — it can only return a span from the context or abstain, which would make the grounding comparison meaningful.

---

## Part C — Debugging Moments

### C1. The Most Frustrating Bug

The most frustrating bug was the notebook throwing `ModuleNotFoundError: No module named 'src'` when run from the `Notebook/` subdirectory. The notebook imports `from src.chunking.tokenizer import TokenizerComparison`, which works when Python's working directory is the project root, but Jupyter sets the working directory to wherever the `.ipynb` file lives — in this case, `Notebook/`, one level below `src/`.

It took about 45 minutes to fix, partly because I initially thought it was a `PYTHONPATH` issue and tried setting environment variables, then tried adding a `setup.py`, before realising the simplest fix was either to move the notebook to the project root or to add `import sys; sys.path.insert(0, '..')` at the top of the notebook. I went with moving the notebook to the project root.

If someone hits this next week: check your working directory first. Run `import os; print(os.getcwd())` in the first notebook cell. If it's not the project root, add `sys.path.insert(0, '/path/to/project/root')` before any local imports.

### C2. What Still Bothers Me

The behavior on Q4 ("What is inertia?") still bothers me. The model output was: *"I don't know as per the given context, but usually, inertia refers to..."* — it refused and then answered in the same sentence. This is the worst possible outcome: the refusal signal is present (so a downstream filter might flag it as a refusal) but the actual answer follows immediately from parametric memory. A student reading this gets the answer; a safety filter checking for "I don't know" might flag it as a correct refusal. It is both a grounding failure and an unreliable signal failure simultaneously.

To fix it I would need to either use a stronger instruction-following model, or add a post-processing step that checks whether the model's output contains "I don't know" followed by substantive content and strips everything after that phrase.

---

## Part D — Architecture and Reasoning

### D1. Why Not Just ChatGPT?

If a hiring manager asked me "why not just use ChatGPT," I would show them Q17 from my evaluation: "Explain Ohm's Law." My system said it could not answer because the context was about How Forces Affect Motion — which is the correct behavior, even if imperfectly executed. ChatGPT would explain Ohm's Law fluently and correctly. For a general-purpose assistant, that is an advantage. For PariShiksha, it is a liability.

The non-negotiable requirement from the scenario is that the assistant must stay grounded in NCERT content. A parent whose daughter asks "explain Ohm's Law" and gets a correct answer from ChatGPT — but one that contradicts how it is taught in the specific NCERT chapter her teacher uses — would escalate. The retrieval system bounds the answer space to the exact corpus the teacher approved. ChatGPT has no such boundary. Additionally, if a student types a question that is in scope but uses slightly different vocabulary than the textbook ("what makes things hard to stop moving?"), a retrieval system can be tuned to match that phrasing to the inertia chunk. ChatGPT would answer from general knowledge, with no guarantee of alignment to the NCERT phrasing that will appear on the exam.

The deeper point is that for grounded, domain-specific, pedagogically consistent QA, retrieval is not a workaround for a weaker model — it is the architectural guarantee that the model's answers stay within approved boundaries.

### D2. The GANs Reflection

GANs work by having two networks compete: a generator tries to produce realistic outputs, and a discriminator tries to distinguish generated from real. The training signal is adversarial — the generator gets better by fooling the discriminator, not by being correct in any absolute sense. This is exactly the wrong property for a bounded textbook assistant.

The problem I am solving is not "generate text that looks like a plausible NCERT answer." It is "extract the correct answer from a specific corpus and present it faithfully." A GAN trained on NCERT text might generate fluent, NCERT-sounding answers — but fluency and correctness are different things. The discriminator cannot tell whether "force equals mass times velocity" is wrong; it can only tell whether it sounds like something from the training set. A GAN could confidently generate a wrong formula in NCERT style and pass its own discriminator.

The deeper principle is: match your training objective to your deployment objective. When the deployment objective is factual accuracy within a bounded domain, you need a system whose output is constrained by the source (retrieval) and whose generation is conditional on that source (grounded LLM prompting). GANs optimise for distributional plausibility, not factual groundedness. These are not the same thing, and using a GAN here would be optimising for the wrong metric entirely.

### D3. Honest Pilot Readiness

Honest answer: **No, we should not launch next Monday.**

My system scored 3/20 correct, 3/20 grounded, and 0/5 appropriate refusals. In a classroom of 100 students, that means most questions will get ungrounded answers, and out-of-scope questions will not be refused reliably. For a use case where a parent calling about a wrong answer could kill the pilot, those numbers are not acceptable.

Three specific things I would want to verify or fix first:

1. **Fix the grounding prompt and verify refusals work.** Change to the constraint phrasing ("refuse if not in context") and rerun the out-of-scope questions. This is a one-day fix that directly addresses the trust failure mode.

2. **Fix the PDF extraction pipeline.** The "Chapter-.indd" artifacts and digit-stripping in `clean_text.py` are corrupting chunks. Switching to PyMuPDF with better page-boundary detection and removing the `re.sub(r'\b\d+\b', '')` line (which destroys physics numbers like 9.8 m/s²) would substantially improve retrieval quality.

3. **Build a human evaluation set, not an LLM-as-judge set.** My current evaluation uses phi3 to judge phi3's answers, which is circular. Before launch I would want the contracted Class 9 Science teacher to manually score at least 50 questions — especially the ones the system currently gets wrong — so we have a reliable signal on whether the system is safe to deploy.

---

## Part E — Effort and Self-Assessment

### E1. Effort Rating

**6 / 10.**

I built the core pipeline — extraction, chunking, BM25, generation, evaluation loop — and got it running end-to-end. That is real work. But I did not run the prompt iteration experiments, did not do the chunk-size comparison, did not attempt any Stretch or Advanced components, and left the submission hygiene (README, requirements.txt, runnable notebook) incomplete until the end. The expert hints in the spec describe exactly the mistakes I made — the permissive prompt phrasing, the circular LLM judge, the untested chunk sizes — and I read them but did not act on all of them in time. That gap between reading and doing is where the missing effort went.

### E2. The Gap Between Me and a Stronger Student

A stronger student would have run the chunk-size experiment with recorded scores at two sizes before settling on 300. I knew this was a Stretch requirement and I changed the chunk size once during development, but I did not save the evaluation output at chunk_size=200 first. The result is that I have an engineering decision (300 > 200) with no quantitative evidence behind it — only an observation that the first version was cutting examples in half. A stronger student would have treated that as a data point to record, not just a problem to fix and move on from.

I did not do it partly because of time and partly because I did not fully internalize the expert hint about single-variable iteration until I was already at the evaluation stage. By then, rerunning everything at two chunk sizes would have cost another two hours I did not have.

### E3. What Would Change with Two More Days

**First thing**: Fix the grounding prompt and rerun the full evaluation. This is the highest-leverage change — it addresses the primary failure mode (0/5 refusals, 3/20 grounded) directly and costs maybe three hours including the rerun. Everything else in the rubric is downstream of whether the system's answers can be trusted.

**Last thing**: Add the dense retrieval comparison (sentence-transformers/all-MiniLM-L6-v2 vs BM25). This is the Advanced tier requirement and it would be genuinely interesting — I expect BM25 to outperform dense retrieval on exact-match queries like "state Newton's second law" but dense retrieval to do better on paraphrased queries like "what makes things hard to stop moving." But it is last because it requires installing new dependencies, integrating a new retrieval class, and rerunning a full evaluation — all of which depend on the grounding and evaluation quality being solid first. Building Advanced features on a broken Base is exactly the failure mode the spec warns against.
