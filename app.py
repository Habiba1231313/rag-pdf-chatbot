import streamlit as st
import pypdf as pdf

st.title("RAG PDF Chatbot")
st.text("Upload a PDF and chat with its content!")
file_object =st.file_uploader("Upload your PDF file", type=["pdf"])
st.write("thanks for uploading ", file_object.name if file_object else "No file uploaded yet.")
question = st.text_input("Ask a question about the PDF content:")
st.button("Submit")

if file_object is not None:
    reader = pdf.PdfReader(file_object)
    st.write("this file has ", len(reader.pages), " pages.")
    for i in range(len(reader.pages)):
        page_text = reader.pages[i].extract_text()
        st.write(page_text[:300])
else:
    st.write("No file uploaded yet.")

