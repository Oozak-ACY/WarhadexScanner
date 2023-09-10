import fitz  # PyMuPDF
import os
import json
import re



def isStringIncomplete(string):
    if len(string)>=1:
        if string[-1] == " ":
            return True
    return False

def isDefinition(string):
    content = string.split(": ")
    if len(content)>1 and len(content[0])>0:
        return True
    return False
        

def findDatasInText(game, type, page_content):
    keywords =""
    fig_keywords = {"keywords": []}  
    fig_wargear = {"wargear": []}
    fig_faction_keywords   = {"faction_keywords": []} 
    fig_abilities = {"abilities": []}
    fig_wargear_abilities = {"wargear_abilities": []}
    fig_stats = {"stats": []}
    i=0
    iterator = 0
    
      
    if i==0:
        fig_name = page_content[0]
        i+=1
    
    temp_keywords = ""
#------------------------------------ OBTENTION DES MOT CLES --------------------------------
    while isStringIncomplete(page_content[i+iterator]):
        iterator+=1
        temp_keywords += page_content[i+iterator]
        
    keywords = page_content[i] + temp_keywords
    keywords = keywords.replace("  ", "")
    keywords = keywords.replace("– ALL MODELS", "")
    keywords = keywords.replace(" – " + fig_name, ", ")
    keywords = keywords.replace("KEYWORDS", "")
    keywords = keywords.replace(": ", "")
    keywords = keywords.split(", ")
    for keyword in keywords:
        fig_keywords["keywords"].append({"keyword":keyword})
#----------------------------------- FIN OBTENTION DES MOT CLES -----------------------------
    i+= iterator + 8
#----------------------------------- OBTENTION ARMES ----------------------------------------    
    while "FACTION KEYWORDS" not in page_content[i]:
        if "MELEE WEAPONS" not in page_content[i] or "RANGED WEAPONS" not in page_content[i]: #ce test permet de passer à +7 i si on detecte le mot afin de ne rentrer que les données interessantes
            iterator=0
            temp_weapon_name = ""
            while isStringIncomplete(page_content[i+iterator]):
                iterator+=1
                temp_weapon_name += page_content[i+iterator]
            
            weapon_name = page_content[i] +  temp_weapon_name
            i+=iterator
            fig_weapon = {weapon_name: []}
            fig_weapon[weapon_name].append({"RANGE":page_content[i+1]})
            fig_weapon[weapon_name].append({"A":page_content[i+2]})
            fig_weapon[weapon_name].append({"WS":page_content[i+3]})
            fig_weapon[weapon_name].append({"S":page_content[i+4]})
            fig_weapon[weapon_name].append({"AP":page_content[i+5]})
            fig_weapon[weapon_name].append({"D":page_content[i+6]})
            fig_wargear["wargear"].append(fig_weapon)
        i=i+7
#------------------------------------ FIN OBTENTION ARMES ----------------------------------
    i+=1
    iterator = 0
#------------------------------------ OBTENTION MOT CLE FACTION --------------------------------
    while "ABILITIES" not in page_content[i]:
        if isStringIncomplete(page_content[i+iterator]):
            iterator+=1 
        else:
            faction_keywords = ""
            for j in range(i,i+iterator+1):
                faction_keywords += page_content[j]
            fig_faction_keywords["faction_keywords"].append({"faction_keyword":faction_keywords})
        i+=1    
#----------------------------------- FIN MOT CLE FACTION -----------------------------------

    i+=1
    iterator = 0
    content = ""
    temp_content = ""
#------------------------------------ OBTENTION COMPETENCES ------------------------------------
    while page_content[i] != "WARGEAR ABILITIES":
        if isStringIncomplete(page_content[i+iterator]):
            iterator+=1
            temp_content += page_content[i+iterator] 
        else:
            content = page_content[i-iterator] + temp_content
            if temp_content:
                i+=1
                temp_content = ""
                iterator = 0
        
        if isDefinition(content):
            abilitie_definition = content.split(": ")
            if "CORE" in abilitie_definition[0]:
                fig_abilities["abilities"].append({"CORE":abilitie_definition[1]})
            else:
                fig_abilities["abilities"].append({abilitie_definition[0]:abilitie_definition[1]})
            content = ""
        i+=1
#----------------------------------- FIN OBTENTION COMPETENCES ---------------------------------

    i+=1

#------------------------------------ OBTENTION COMPETENCES EQUIPEMENT------------------------------------
    while page_content[i] != "M":
        if isStringIncomplete(page_content[i+iterator]):
            iterator+=1
            temp_content += page_content[i+iterator] 
        else:
            content = page_content[i-iterator] + temp_content
            if temp_content:
                temp_content = ""
                iterator = 0
        
        if isDefinition(content):
            abilitie_definition = content.split(": ")
            fig_wargear_abilities["wargear_abilities"].append({abilitie_definition[0]:abilitie_definition[1]})
            content = ""
        i+=1
#----------------------------------- FIN OBTENTION COMPETENCES EQUIPEMENT ---------------------------------
    i+=6
    iterator = 0
    nb_stats = 6 #il y a 6 statistiques à enregistrer   
#----------------------------------- OBTENTION STATS ------------------------------------------------------
    while i<=len(page_content):
        while bool(re.search(r'\d', page_content[i+iterator])):
            iterator+=nb_stats
            content = page_content[i+iterator]
        nb_substats = int(iterator/nb_stats)
        temp_iterator = nb_substats-1
        for j in range(0, nb_substats):
            substat_name = page_content[i+iterator+temp_iterator]
            fig_substat = {substat_name: []}
            fig_substat[substat_name].append({"M":page_content[i+(nb_stats*j)]})
            fig_substat[substat_name].append({"T":page_content[i+(nb_stats*j)+1]})
            fig_substat[substat_name].append({"SV":page_content[i+(nb_stats*j)+2]})
            fig_substat[substat_name].append({"W":page_content[i+(nb_stats*j)+3]})
            fig_substat[substat_name].append({"LD":page_content[i+(nb_stats*j)+4]})
            fig_substat[substat_name].append({"OC":page_content[i+(nb_stats*j)+5]})
            fig_stats["stats"].append(fig_substat)
            temp_iterator-=1    
            
        i+=1    
#----------------------------------- FIN OBTENTION STATS ---------------------------------------------------
    x=i 
    

def extraction40K(document):
    first_fig_page_modulo = ""
    nbFig = 0
    x=0

    # Boucle sur toutes les pages du PDF
    for page_num in range(document.page_count):
        # Obtenir l'objet Page de la page actuelle
        page = document.load_page(30)   
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
            if is_front_card:
                filter_keys = [item["key"] for item in data["content_keys_front"]]
            else:
                filter_keys = [item["key"] for item in data["content_keys_rear"]]
                
            findDatasInText("40k", is_front_card, page_content)     
            
            
            
            
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