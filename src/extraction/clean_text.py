import PyPDF2
import re
import os

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
    

if __name__ == "__main__":
    input_path = r"F:\Projects\retrieval-study-assistant\Data\Processed\iesc106.txt"
    output_path = r"F:\Projects\retrieval-study-assistant\Data\Processed\cleaned.txt"

    # Read file
    with open(input_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # Clean text
    cleaner = TextCleaner(raw_text)
    cleaned_text = cleaner.clean()

    # Save output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cleaned_text)

    print(f"Saved to {output_path}")