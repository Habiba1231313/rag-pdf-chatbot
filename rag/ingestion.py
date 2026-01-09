import pypdf as pdf

def extract_text_from_pdf(file):
    reader = pdf.PdfReader(file)
    pages = []

    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""  # ensure string
        if text.strip():  # only keep pages that actually have text
            pages.append({"PageNumber": page_num, "Text": text})

    return pages
