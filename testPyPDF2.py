import PyPDF2

def isVerticale(page):
    page_dimensions = page.mediabox
    page_height = page_dimensions.top
    page_width = page_dimensions.right
    if page_height < page_width:
        return False
    return True


        

# Définir le chemin vers le fichier PDF que vous souhaitez analyser
pdf_path = 'D:\\DEV\\Projets\\Github\\WarhadexScanner\\images\\tauindex.pdf'

# Ouvrir le fichier PDF en mode lecture binaire
with open(pdf_path, 'rb') as pdf_file:
    # Créer un objet PyPDF2 pour lire le PDF
    pdf_reader = PyPDF2.PdfReader(pdf_file)

    # Boucle sur toutes les pages du PDF
    for page_num in range(len(pdf_reader.pages)):
        # Obtenir l'objet PageObject pour la page actuelle
        page = pdf_reader.pages[57]
        
        if isVerticale(page) == False:
            texte_page = page.extract_text().split("\n")
            


        