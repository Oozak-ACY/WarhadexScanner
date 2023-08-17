import fitz  # PyMuPDF
import os
import json



def isStringIncomplete(string):
    if len(string)>=1:
        if string[-1] == " ":
            return True
    return False

def findDatasInText(game, type, page_content):
    keywords =""
    fig_keywords = {"keywords": []}  
    fig_wargear = {"wargear": []}
    fig_faction_keywords   = {"faction_keywords": []}
    fig_abilities = {"abilities": []} 
    x=0  
    if x==0:
        fig_name = page_content[0] 
    for i in range(1,x):
        keywords = keywords + page_content[i]
    keywords = keywords.replace("KEYWORDS:  ", "").split(", ")
    for keyword in keywords:
        fig_keywords["keywords"].append({"keyword":keyword})
    i=x+7
    while "FACTION KEYWORDS" not in page_content[i]:
        if "MELEE WEAPONS" not in page_content[i]:
            weapon_name = page_content[i]
            fig_weapon = {weapon_name: []}
            fig_weapon[weapon_name].append({"RANGE":page_content[i+1]})
            fig_weapon[weapon_name].append({"A":page_content[i+2]})
            fig_weapon[weapon_name].append({"WS":page_content[i+3]})
            fig_weapon[weapon_name].append({"S":page_content[i+4]})
            fig_weapon[weapon_name].append({"AP":page_content[i+5]})
            fig_weapon[weapon_name].append({"D":page_content[i+6]})
            fig_wargear["wargear"].append(fig_weapon)
        i=i+7
    i+=1
    iterator = 0
    while "ABILITIES" not in page_content[i]:
        if isStringIncomplete(page_content[i+iterator]):
            iterator+=1 
        else:
            faction_keywords = ""
            for j in range(i,i+iterator+1):
                faction_keywords += page_content[j]
            fig_faction_keywords["faction_keywords"].append({"faction_keyword":faction_keywords})
        i+=1     
    while page_content[i] != "M":
                
    x=i 
    

def extraction40K(document):
    first_fig_page_modulo = ""
    nbFig = 0

    # Boucle sur toutes les pages du PDF
    for page_num in range(document.page_count):
        # Obtenir l'objet Page de la page actuelle
        page = document.load_page(page_num)   
        if isHorizontale(page):
            # Si la variable est vide alors rempli la variable avec le modulo du numéro de page
            # Ceci est fait afin de savoir si la première page de stat fig est paire ou impaire
            if first_fig_page_modulo=="":
                first_fig_page_modulo = page_num%2
            
            actual_fig_page_modulo = page_num%2
                
            # Si le modulo du numéro de page actuel est égal à celui de la première feuille alors c'est la face de la carte de fig     
            if actual_fig_page_modulo == first_fig_page_modulo:
                is_front_card = True
            else:
                is_front_card = False
                
            page_content = page.get_text().split("\n")
            
            # Chemin d'accès complet au fichier JSON
            file_name = "40k" + ".json"
            json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)) + "\\jsons\\", file_name)
            # Charger les données du fichier JSON
            with open(json_path, "r") as json_file:
                data = json.load(json_file)
            if type:
                filter_keys = [item["key"] for item in data["content_keys_front"]]
            else:
                filter_keys = [item["key"] for item in data["content_keys_rear"]]
                
            
            while x<len(page_content):

                if type:
                    if "RANGED WEAPONS" in page_content[x]:
                       findDatasInText("40k", is_front_card, page_content) 
        
                x+=1    
            
            
            
            # Si la page actuelle est la face de la carte
            if is_front_card:
                nbFig+=1
                print(page_content[0])
                
            else:
                test="oui"
    print(f"{nbFig} figs ont été traitées")

                
def exportJson(game):
    dir_jsons = os.path.dirname(os.path.abspath(__file__)) + "\\jsons\\"
    files = [file for file in os.listdir(dir_jsons) if file.endswith(".json")]
    json_file_name = game + "figs.json"
    dir_json_file = os.path.join(dir_jsons, json_file_name)
    for file in files:
        if file == json_file_name:
            return
    data = {
        "factions": [
        ]
    }

    with open(dir_json_file, "w") as json_file:
        json.dump(data, json_file, indent=4)
    

            
            
 

def isHorizontale(page):
    page_dimensions = page.rect
    page_height = page_dimensions.height
    page_width = page_dimensions.width
    if page_height > page_width:
        return False
    return True

def extractionMain(game):
    dir_import = os.path.dirname(os.path.abspath(__file__)) + "\\imports\\"
    # Obtient la liste de tous les fichiers dans le répertoire 'imports'
    files = [file for file in os.listdir(dir_import) if file.endswith(".pdf")]
    
    for file in files:
        # Ouvrir le fichier PDF avec PyMuPDF
        pdf_document = fitz.open(dir_import + "\\" +file)
        match(game):
            case "40k":
                exportJson(game)
                extraction40K(pdf_document)

        # Fermer le document PDF
        pdf_document.close()
            
extractionMain("40k")