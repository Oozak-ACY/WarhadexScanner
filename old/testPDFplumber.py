import pdfplumber

pdf_path = 'C:\\Projets\\www\\Github\\WarhadexScanner\\imports\\tauindex.pdf'

try:
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[24]
        text = page.extract_text()
        text=text.split("\n")
        print(text)
except Exception as e:
    print(f"Une erreur s'est produite : {e}")