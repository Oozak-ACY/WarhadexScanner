import fitz  # PyMuPDF
import os
import json
import re


class PDFPage:
    
    def __init__(self, page_object):
        self.page_object = page_object
        self.front_content_limits_keys = ["FACTION KEYWORDS", "RANGED WEAPONS", "MELEE WEAPONS", "WARGEAR ABILITIES", "ABILITIES", "KEYWORDS", "DAMAGED", "INVULNERABLE SAVE"]
        self.weapons_stats_limits_keys = ["RANGE", "A","BS","S","AP", "D"]
        self.fig_stats_limits_keys = ["M", "T", "SV", "W", "W","LD","OC"]

        
    def isDefinition(self, string):
        content = string.split(": ")
        if len(content)>1 and len(content[0])>0:
            return True
        return False
    
    def isHorizontale(self):
        page_dimensions = self.page_object.rect
        page_height = page_dimensions.height
        page_width = page_dimensions.width
        if page_height > page_width:
            return False
        return True
    
    def isStringIncomplete(self, string):
        if len(string)>=1:
            if string[-1] == " ":
                return True
        return False
    
    def getText(self):
        return self.page_object.get_text()
    
    def parseText(self):
        page_content = self.getText().split("\n")
        x=0
        xIsDefinition = False
        while x<len(page_content):
            if self.isStringIncomplete(page_content[x]):
                if page_content[x+1] == 'Melee' or '"' in page_content[x+1] or xIsDefinition:
                    page_content[x] = page_content[x][:len(page_content[x])-1]
                    
                else:
                    if not self.isDefinition(page_content[x+1]):
                        page_content[x] += page_content[x+1]
                        page_content[x] = page_content[x].replace("  ", " ")
                        page_content.pop(x+1)
                    else:
                        xIsDefinition = True
            else:
                xIsDefinition = False
                x+=1
        self.page_content = page_content
        
    
    def isStringInALimitsKey(self, type, string):
        if self.isDefinition(string):
            string = string.split(":")
            string = string[0]
        match type:
            case 0:
                for element in self.front_content_limits_keys:
                    if element in string:
                        return element
            case 1:
                for element in self.weapons_stats_limits_keys:
                    if element == string:
                        return element
            case 2:
                for element in self.fig_stats_limits_keys:
                    if element == string:
                        return element
            case _:
                return False

    
    def getContentLimits(self):
        self.parseText()
        page_content = self.page_content
        x=0
        limits = {}
        last_limits_key = ""
        stats_last_limits_key = ""
        
        while x<len(page_content):
            line = page_content[x]
            
                
            # Si la chaine contient un element de front content limit key alors rentre les valeurs de bornages du contenu concerné
            if self.isStringInALimitsKey(0, line):
                limits_key = self.isStringInALimitsKey(0, line)
                self.front_content_limits_keys.remove(limits_key)
                if last_limits_key:
                    limits[last_limits_key].append(x)
                elif x!=0:
                    limits["NAME"] = [0, x]
                if limits_key not in limits:
                    last_limits_key = limits_key
                    limits[limits_key] = []
                    limits[limits_key].append(x)
            elif last_limits_key in ["MELEE WEAPONS", "RANGED WEAPONS"] and self.isDefinition(page_content[x+1]) and x+1<len(page_content):
                while self.isStringIncomplete(page_content[x+1]):
                    page_content[x+1] = page_content[x] +page_content[x+2]
                    page_content.pop(x+2)
                page_content.pop(x+1)
                
            
            # Si la chaine contient un element de fig stats limit key alors rentre les valeurs de bornages du contenu concerné        
            if self.isStringInALimitsKey(2, line):
                if not stats_last_limits_key and last_limits_key:
                    limits[last_limits_key].append(x)
                last_limits_key = "STATS"
                if last_limits_key not in limits:
                    limits[last_limits_key] = []
                    limits[last_limits_key].append(x)
                    stats_last_limits_key = "STATS"
            
                
            
            # Si on a atteint la derniere chaine et que ce n'est pas un clé de bornage alors note l'indice dans la dernière clé concernée      
            if x+1 == len(page_content) and not self.isStringInALimitsKey(-1, line):
                if last_limits_key:
                    limits[last_limits_key].append(len(page_content))
                    
                           
            x+=1
            
        # # Permet d'ajouter le nom de la carte dans le tableau ainsi que les indices de bornage
        # limits_keys_values = list(limits.values())
        # first_key_values = limits_keys_values[0]
        # if first_key_values[0]>0:
        #     limits["NAME"] = [0, first_key_values[0]]
        
        return limits
    
    
    
    def extractDatas(self):
        content_limits = self.getContentLimits()
        page_content = self.page_content
        content_keys = list(content_limits.keys())
        content_values = list(content_limits.values())
        fig = Figurine()


        
        for part_name, keys in content_limits.items():
            start_index = keys[0]
            end_index = keys[1]
            limit_key_iterator = 0
            x_weapon_stats_iterator = 0
            weapon_limit_key = []
            weapon_stats = {}
            for x in range(start_index, end_index):
                content = page_content[x]
                
                if part_name in ["MELEE WEAPONS", "RANGED WEAPONS"]:
                    content = content.lstrip()
                    if limit_key_iterator == len(fig.weapon_stat_key)-1:
                        if x_weapon_stats_iterator%limit_key_iterator == 0:
                            weapon_stats[content] = []
                            last_weapon_name = content
                            x_weapon_stats_iterator = 0
                        else:
                            weapon_stats[last_weapon_name].append({weapon_limit_key[x_weapon_stats_iterator-1]: content})
                        x_weapon_stats_iterator +=1
                    else:
                       if fig.isWeaponStatKey(content):
                            limit_key_iterator+=1
                            weapon_limit_key.append(content)  
                elif part_name in ["KEYWORDS", "FACTION KEYWORDS"]:
                    fig.setNewKeyword(content, part_name)
                elif part_name == "NAME":
                    fig.setName(content)
                elif part_name == "ABILITIES":
                    if x != start_index:
                        if "CORE" in content or "FACTION" in content:
                            abilitie_line = content.split(":")
                            abilities = abilitie_line[1].split(",")
                            for abilitie in abilities:
                                # Si le premier caractère de abilitie est un espace, supprimer celui-ci
                                if abilitie[0] == " ":
                                    abilitie = abilitie[1:] 
                                fig.setNewAbilities(abilitie, abilitie_line[0])
                        else:
                            abilitie_line = content.split(":")
                            # Si le premier caractère de abilitie est un espace, supprimer celui-ci
                            if abilitie_line[1][0] == " ":
                                abilitie_line[1] = abilitie_line[1][1:]
                            fig.setNewAbilities(abilitie_line[1], abilitie_line[0])
        stopvar=0
    
    
    
class Figurine:

    def __init__(self):
        self.name = ""
        self.keywords = {}
        self.weapons = {}
        self.abilities = {}
        self.stats = {}
        self.weapon_stat_key = ["RANGE", "A", "BS", "S", "AP", "D", "WS"]
        self.fig_stat_key = ["M", "T", "SV","W","LD","OC"]
        
    def setName(self, name):
        self.name = name
    
    def setNewKeyword(self, keyword, type):
        if type not in self.keywords:
            self.keywords[type] = []
        keywords = keyword
        keywords = keywords.replace("  ", "")
        keywords = keywords.replace("– ALL MODELS", "")
        keywords = keywords.replace(" – " + self.name, ", ")
        keywords = keywords.replace(type, "")
        keywords = keywords.replace(": ", "")
        keywords = keywords.split(", ")
        for part in keywords:
            self.keywords[type].append(part)
    
    def isWeaponStatKey(self, string):
        for element in self.weapon_stat_key:
            if string == element:
                return True
        return False
    
    def isFigStatKey(self, string):
        for element in self.fig_stat_sey:
            if string == element:
                return True
        return False
    
    def setNewWeapon(self, weapon, type):
        if type not in self.weapons:

            self.weapons[type] = []
        self.weapons[type].append(weapon)
    
    def setNewAbilities(self, abilitie, abilitie_name):
        if abilitie_name not in self.abilities:
            self.abilities[abilitie_name] = []
        self.abilities[abilitie_name].append(abilitie)
    
    def setStats(self, stats):
        self.abitilies["STATS"].append(stats)

    
class PDFFile:
    
    def __init__(self, document):
        self.document = document
    
    def getTotalPage(self):
        return self.document.page_count
    

    
    def extractDataFromPdf(self):
        nb_pages = self.getTotalPage()
        first_horizontale_page = False
        for x_page in range(nb_pages):
            page = PDFPage(self.document.load_page(60))
            if page.isHorizontale():
                if not first_horizontale_page:
                    first_horizontale_page = x_page
                    
                # Condition qui permet de sauter les pages verso des cartes
                if x_page%2 == first_horizontale_page%2:
                    page.extractDatas()
                
                

class PDFParser:
    
    def __init__(self, path, input):
        self.path = path
        self.input = input
        
    def getPdfFiles(self):
        files = [file for file in os.listdir(self.path) if file.endswith(".pdf")] 
        return files
    
    def parseAll(self):
        # try:
        files = self.getPdfFiles()
        for file in files:
            pdf_document = fitz.open(self.path + "\\" + file)
            pdf_file = PDFFile(pdf_document)
            pdf_file.extractDataFromPdf()
        return True
        # except Exception as e:
        #     print(f"Une erreur s'est produite : {e}")
        #     return False
        
    def parseOne(self):
        try:
            pdf_document = fitz.open(self.path + "\\" + self.input)
            pdf_file = PDFFile(pdf_document)
            
            return True
        except Exception as e:
            print(f"Une erreur s'est produite : {e}")
            return False
        
class DataProcessing:
    
    def __init__(self, path):
        self.path = path

    

dir_import = os.path.dirname(os.path.abspath(__file__)) + "\\imports\\"
pdf_manager = PDFParser(dir_import, '')

var1 = pdf_manager.parseAll()

exvar = 0

 