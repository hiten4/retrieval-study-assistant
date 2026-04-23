import PyPDF2

class PDFLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load(self):
        text = ""

        with open(self.file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)

            for i, page in enumerate(reader.pages):
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"

        return text


if __name__ == "__main__":
    loader = PDFLoader(r"F:\Projects\retrieval-study-assistant\Data\Raw\iesc106.pdf")
    data = loader.load()
    # print(data[:1000])  
    output_path = r"F:\Projects\retrieval-study-assistant\Data\Processed\iesc106.txt"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(data)

    print(f"Saved to {output_path}")
