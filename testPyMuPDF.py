import fitz  # PyMuPDF

def isVerticale(page):
    page_dimensions = page.rect
    page_height = page_dimensions.height
    page_width = page_dimensions.width
    if page_height > page_width:
        return True
    return False

# Définir le chemin vers le fichier PDF que vous souhaitez analyser
pdf_path = 'D:\\DEV\\Projets\\Github\\WarhadexScanner\\images\\tauindex.pdf'

# Ouvrir le fichier PDF avec PyMuPDF
pdf_document = fitz.open(pdf_path)

# Boucle sur toutes les pages du PDF
for page_num in range(pdf_document.page_count):
    # Obtenir l'objet Page de la page actuelle
    page = pdf_document.load_page(57)

    if isVerticale(page) == False:
        texte_page = page.get_text().split("\n")


        

    

# Fermer le document PDF
pdf_document.close()