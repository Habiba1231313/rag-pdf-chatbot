import streamlit as st

st.title("RAG PDF Chatbot")
st.text("Upload a PDF and chat with its content!")
file =st.file_uploader("Upload your PDF file", type=["pdf"])
st.write("thanks for uploading ", file.name if file else "No file uploaded yet.")
question = st.text_input("Ask a question about the PDF content:")
st.button("Submit")




