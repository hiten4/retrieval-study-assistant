import ollama


class LLMGenerator:
    def __init__(self, model_name):
        self.model = model_name

    def generate(self, question, context):
        prompt = f"""
You are a NCERT study assistant.

STRICT RULES:
- Answer ONLY from the provided context
- If answer is not in context, say "I don't know"
- Do NOT add external knowledge

Context:
{context}

Question:
{question}
"""

        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )

        return response["message"]["content"]