# Function to chunk text (chunk-aware + metadata)
def chunk_text(pages,filename, chunk_size=1000, overlap=200):
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must satisfy 0 <= overlap < chunk_size")

    chunks = []
    chunk_id = 0
    step = chunk_size - overlap

    for page in pages:
        text = page["Text"]
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]

            if chunk_text.strip():  # skip empty/whitespace chunks
                chunks.append( {
                    "chunkId": chunk_id,
                    "text": chunk_text,
                    "PageNumber": page["PageNumber"],
                    "FileName" : filename,
                })
                chunk_id += 1

            start += step

    return chunks