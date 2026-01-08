import streamlit as st
import pypdf as pdf

#Function to extract text from PDF
def extract_text_from_pdf(file):
    reader = pdf.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    if text is not None:
        return text,len(reader.pages)
    return "NO TEXT FOUND",0

def chunk_text(text, chunk_size=1000, overlap=200):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks

        
    

# Streamlit app
st.title("RAG PDF Chatbot")
st.text("Upload a PDF and chat with its content!")
file_object =st.file_uploader("Upload your PDF file", type=["pdf"])
st.write("thanks for uploading ", file_object.name if file_object else "No file uploaded yet.")
question = st.text_input("Ask a question about the PDF content:")
st.button("Submit") 

if file_object is not None:
    text, num_pages = extract_text_from_pdf(file_object)
    st.write("this file has ", num_pages, " pages.")
    st.write("number of characters in the pdf text:", len(text))
    chunks = chunk_text(text)
    st.write("number of chunks created:", len(chunks))
else:
    st.write("No file uploaded yet.")



