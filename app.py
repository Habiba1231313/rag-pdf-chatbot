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


openai.api_key = st.secrets["OPENAI_API_KEY"]



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



st.set_page_config(
    page_title="RAG PDF Chatbot",
    page_icon="📄",
    layout="wide",
)

# ---------- Header ----------
st.title("📄 RAG PDF Chatbot")
st.caption("Upload a PDF, ask questions, and get grounded answers with citations.")

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Controls")
    file_object = st.file_uploader("Upload PDF", type=["pdf"])
    top_k = st.slider("Top-k chunks", min_value=1, max_value=8, value=3)
    show_context = st.checkbox("Show retrieved chunks", value=False)
    st.divider()
    st.subheader("Status")
    status_box = st.empty()

# ---------- Main layout ----------
col_left, col_right = st.columns([1.15, 0.85], gap="large")

with col_left:
    st.subheader("❓ Ask a question")
    question = st.text_input("Type your question here", placeholder="e.g., What is the grading breakdown?")
    ask = st.button("Ask", type="primary", use_container_width=True)

with col_right:
    st.subheader("📌 Document summary")
    metrics_cols = st.columns(3)
    pages_metric = metrics_cols[0].empty()
    chunks_metric = metrics_cols[1].empty()
    cached_metric = metrics_cols[2].empty()

st.divider()

# ---------- Chat history ----------
if "chat" not in st.session_state:
    st.session_state.chat = []  # list of {"q":..., "a":...}

def render_chat():
    if not st.session_state.chat:
        st.info("Upload a PDF and ask a question to start.")
        return
    for item in st.session_state.chat[::-1]:
        with st.container(border=True):
            st.markdown("**You:**")
            st.write(item["q"])
            st.markdown("**Answer:**")
            st.write(item["a"])

# ---------- Your existing doc_cache init ----------
if "doc_cache" not in st.session_state:
    st.session_state.doc_cache = {}

# ---------- Document processing + caching ----------
chunks = None
is_cached = False

if file_object:
    file_key = file_object.name
    if file_key in st.session_state.doc_cache:
        is_cached = True
        chunks = st.session_state.doc_cache[file_key]["chunks"]
        pages = st.session_state.doc_cache[file_key]["pages"]
        status_box.success("Using cached embeddings ⚡")
    else:
        status_box.info("Processing document…")
        with st.spinner("Extracting text, chunking, and embedding…"):
            pages = extract_text_from_pdf(file_object)
            chunks = chunk_text(pages, file_object.name)
            chunks = embed_chunks(chunks)
            st.session_state.doc_cache[file_key] = {"pages": pages, "chunks": chunks}
        status_box.success("Document processed and cached ✅")

    pages_metric.metric("Pages", len(pages))
    chunks_metric.metric("Chunks", len(chunks))
    cached_metric.metric("Cached", "Yes" if is_cached else "No")
else:
    status_box.warning("Upload a PDF to begin.")
    pages_metric.metric("Pages", "-")
    chunks_metric.metric("Chunks", "-")
    cached_metric.metric("Cached", "-")

# ---------- Q&A ----------
if ask:
    if not file_object:
        st.error("Please upload a PDF first.")
    elif not question.strip():
        st.error("Please type a question.")
    else:
        with st.spinner("Retrieving context and generating answer…"):
            q_embed = embed_query(question)
            scored = add_similarity_scores(chunks, q_embed)
            top_chunks = top_k_chunks(scored, k=top_k)

            prompt = build_prompt(top_chunks, question)
            answer = generate_answer(prompt)

        # Save to chat history
        st.session_state.chat.append({"q": question, "a": answer})

        # Show answer prominently
        st.subheader("🧠 Answer")
        st.success("Done ✅")
        st.write(answer)

        # Optional: show retrieved chunks
        if show_context:
            with st.expander("🔍 Retrieved chunks (context used)", expanded=False):
                for c in top_chunks:
                    st.markdown(
                        f"**Score:** {c['similarity_score']:.4f}  •  "
                        f"**{c['FileName']}**  •  **Page {c['PageNumber']}**"
                    )
                    st.write(c["text"][:500] + "…")
                    st.divider()

st.subheader("💬 History")
render_chat()