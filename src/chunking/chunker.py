import re

class Chunker:
    def __init__(self, text, chunk_size, overlap):
        self.text = text
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split_sentences(self):
        sentences = re.split(r'(?<=[.!?])\s+', self.text)
        return sentences

    def create_chunks(self):
        sentences = self.split_sentences()

        chunks = []
        current_chunk = []

        for sentence in sentences:
            words = sentence.split()

            # if adding sentence exceeds chunk size → save chunk
            if len(current_chunk) + len(words) > self.chunk_size:
                chunks.append(" ".join(current_chunk))

                # overlap handling (last N words)
                overlap_words = current_chunk[-self.overlap:]
                current_chunk = overlap_words.copy()

            current_chunk.extend(words)

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