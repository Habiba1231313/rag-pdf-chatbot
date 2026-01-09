import streamlit as st
import pypdf as pdf
import openai
from rag.ingestion import extract_text_from_pdf
from rag.chunking import chunk_text
from rag.embeddings import embed_query, embed_chunks
from rag.retrieval import add_similarity_scores, top_k_chunks
import os


if "authed" not in st.session_state:
    st.session_state.authed = False

if not st.session_state.authed:
    st.title("RAG PDF Chatbot 🔒")
    pw = st.text_input("Password", type="password")
    if st.button("Enter"):
        if pw == st.secrets["APP_PASSWORD"]:
            st.session_state.authed = True
            st.rerun()
        else:
            st.error("Wrong password.")
    st.stop()


openai.api_key = os.getenv("api key")

openai.api_key = "api key"


def build_prompt(top_chunks, question):
    context_parts = []

    for c in top_chunks:
        context_parts.append(
            f"File: {c['FileName']}, Page: {c['PageNumber']}\n"
            f"{c['text']}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are a helpful assistant.
Answer the question using ONLY the information from the context below.
If the answer is not in the context, say: "I could not find this in the document."
Cite your answer using (FileName, PageNumber).

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
""".strip()

    return prompt

def generate_answer(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a careful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    return response["choices"][0]["message"]["content"]



if "doc_cache" not in st.session_state:
    st.session_state.doc_cache = {}

# ---------------- UI ----------------
st.title("RAG PDF Chatbot")
st.text("Upload a PDF and chat with its content!")

file_object = st.file_uploader("Upload your PDF file", type=["pdf"])
question = st.text_input("Ask a question about the PDF content:")

# ---------------- LOGIC ----------------
if file_object:
    file_key = file_object.name

    # -------- INGEST + EMBED ONCE --------
    if file_key not in st.session_state.doc_cache:
        pages = extract_text_from_pdf(file_object)
        chunks = chunk_text(pages, file_object.name)
        chunks = embed_chunks(chunks)

        st.session_state.doc_cache[file_key] = {
            "pages": pages,
            "chunks": chunks,
        }

        st.success("Document processed and cached ✅")

    else:
        st.info("Using cached document embeddings ⚡")

    chunks = st.session_state.doc_cache[file_key]["chunks"]

    if question:
        question_embeded = embed_query(question)
        chunks = add_similarity_scores(chunks,question_embeded)
        top_chunks = top_k_chunks(chunks)
        prompt = build_prompt(top_chunks, question)
        answer = generate_answer(prompt)

        st.subheader("Answer")
        st.write(answer)











