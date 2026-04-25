import json
from main import answer
from src.generation.llm import LLMGenerator

# 🔹 Judge model (fast)
judge = LLMGenerator(model_name="phi3:mini")


# ---------------- LLM EVALUATOR ---------------- #

def evaluate_with_llm(question, ans, chunks):
    context = "\n\n".join(chunks)

    prompt = f"""
You MUST return JSON exactly like this:

{{
  "correctness": "yes/no/partial",
  "grounding": "yes/no",
  "refusal": "yes/no/na"
}}

Do not change keys.

Question: {question}
Answer: {ans}
Context: {context}
"""

    response = judge.generate(question="", context=prompt)

    # 🔹 Clean response (important)
    response = response.strip()

    if "```" in response:
        response = response.split("```")[1]

    try:
        data = json.loads(response)

        return {
            "correctness": data.get("correctness", "partial"),
            "grounding": data.get("grounding", "no"),
            "refusal": data.get("refusal", "na")
        }

    except:
        # fallback if parsing fails
        return {
            "correctness": "partial",
            "grounding": "no",
            "refusal": "na"
        }


# ---------------- QUESTIONS ---------------- #

questions = [
    # Direct
    "What is force?",
    "What are the effects of force on an object?",
    "What is Newton’s First Law of Motion?",
    "What is inertia?",
    "What are the different types of inertia?",
    "What is momentum?",
    "State Newton’s Second Law of Motion.",
    "What is the formula for force according to Newton’s Second Law?",
    "What is Newton’s Third Law of Motion?",
    "What is action and reaction?",
    "Why does a passenger fall forward when a moving bus stops suddenly?",
    "Why do we pull our hands back quickly after touching a hot object?",

    # Paraphrased
    "Define force in simple terms.",
    "Why does a body resist change in motion?",
    "Explain Newton’s second law in your own words.",

    # Out-of-scope
    "What is photosynthesis?",
    "Explain Ohm’s Law.",
    "Who discovered gravity?",
    "What is the capital of India?",
    "Explain quantum entanglement in Chapter 6."
]


# ---------------- MAIN EVALUATION ---------------- #

def evaluate():
    results = []

    for q in questions:
        ans, chunks = answer(q)

        eval_result = evaluate_with_llm(q, ans, chunks)

        print("\n======================")
        print("Q:", q)
        print("A:", ans)
        print("Eval:", eval_result)

        results.append({
            "question": q,
            "answer": ans,
            "correctness": eval_result.get("correctness", "partial"),
            "grounding": eval_result.get("grounding", "no"),
            "refusal": eval_result.get("refusal", "na")
        })

    return results


# ---------------- SAVE MARKDOWN ---------------- #

def save_md(results):
    with open("evaluation_results.md", "w", encoding="utf-8") as f:
        f.write("# Evaluation Results\n\n")
        f.write("| Question | Correctness | Grounding | Refusal |\n")
        f.write("|----------|------------|----------|---------|\n")

        for r in results:
            f.write(f"| {r['question']} | {r['correctness']} | {r['grounding']} | {r['refusal']} |\n")


# ---------------- RUN ---------------- #

if __name__ == "__main__":
    results = evaluate()
    save_md(results)
    print("\n Evaluation completed and saved to evaluation_results.md")