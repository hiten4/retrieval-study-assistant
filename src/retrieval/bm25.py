from rank_bm25 import BM25Okapi

class BM25Retriever:
    def __init__(self, chunks):
        self.chunks = chunks
        self.tokenized_chunks = [c.split() for c in chunks]
        self.bm25 = BM25Okapi(self.tokenized_chunks)

    def retrieve(self, query, top_k=3):
        tokenized_query = query.split()
        scores = self.bm25.get_scores(tokenized_query)

        top_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:top_k]

        return [self.chunks[i] for i in top_indices]