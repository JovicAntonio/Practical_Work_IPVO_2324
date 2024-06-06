import fitz  # PyMuPDF

def pdf2text(pdf_path):
    pdf_document = fitz.open(pdf_path)
    
    text = ""
    
    for page_num in range(5, 10):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    
    return text