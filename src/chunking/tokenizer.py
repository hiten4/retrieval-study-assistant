from transformers import AutoTokenizer

class TokenizerComparison:
    def __init__(self):
        self.gpt2 = AutoTokenizer.from_pretrained("gpt2")
        self.bert = AutoTokenizer.from_pretrained("bert-base-uncased")
        self.t5 = AutoTokenizer.from_pretrained("t5-small")

    def compare(self, text):
        return {
            "gpt2_tokens": len(self.gpt2.tokenize(text)),
            "bert_tokens": len(self.bert.tokenize(text)),
            "t5_tokens": len(self.t5.tokenize(text))
        }