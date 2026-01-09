import openai
# Function to embed chunks
def embed_chunks(chunks):
    for chunk in chunks:
       response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=chunk["text"]) 
       chunk["embedding"] = response["data"][0]["embedding"]
       

    return chunks
    

def embed_query (question):
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input= question)
    return response["data"][0]["embedding"]