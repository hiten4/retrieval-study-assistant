import re

class TextCleaner:
    def __init__(self, text):
        self.text = text

    def clean(self):
        text = self.text

        # remove multiple spaces
        text = re.sub(r'\s+', ' ', text)

        # remove page numbers (common pattern)
        text = re.sub(r'\b\d+\b', '', text)

        # fix broken newlines
        text = text.replace('. ', '.\n')

        # remove weird characters
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)

        return text.strip()