import re


class Chunker:
    def __init__(self, text, chunk_size=300, overlap=50):
        self.text = text
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split_sentences(self):
        # split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', self.text)
        return sentences

    def create_chunks(self):
        sentences = self.split_sentences()

        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            words = sentence.split()
            length = len(words)

            if current_length + length > self.chunk_size:
                chunks.append(" ".join(current_chunk))

                # overlap handling
                overlap_words = current_chunk[-self.overlap:] if len(current_chunk) > self.overlap else current_chunk
                current_chunk = overlap_words.copy()
                current_length = len(current_chunk)

            current_chunk.extend(words)
            current_length += length

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks
if __name__ == "__main__":
    with open(r"F:\Projects\retrieval-study-assistant\Data\Processed\cleaned.txt", "r", encoding="utf-8") as f:
        text = f.read()

    chunker = Chunker(text, chunk_size=300, overlap=50)
    chunks = chunker.create_chunks()

    print(f"Total chunks: {len(chunks)}")
    print(chunks[0])