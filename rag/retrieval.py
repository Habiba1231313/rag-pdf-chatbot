from sklearn.metrics.pairwise import cosine_similarity

def add_similarity_scores(chunks, query_embedding):
    for chunk in chunks:
        score = cosine_similarity(
            [query_embedding], 
            [chunk["embedding"]]
        )[0][0]          # <-- extract scalar
        chunk["similarity_score"] = score
    return chunks

def top_k_chunks(chunks, k=3):
    return sorted(chunks, key=lambda c: c["similarity_score"], reverse=True)[:k]
