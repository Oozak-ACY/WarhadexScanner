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
        while x<len(page_content):
            if self.isStringIncomplete(page_content[x]):
                if page_content[x+1] == 'Melee':
                    page_content[x] = page_content[x][:len(page_content[x])-1]
                else:
                    page_content[x] += page_content[x+1]
                    page_content[x] += page_content[x].replace("  ", " ")
                    page_content.pop(x+1)
            else:
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
                if limits_key not in limits:
                    last_limits_key = limits_key
                    limits[limits_key] = []
                    limits[limits_key].append(x)
            
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
            
        # Permet d'ajouter le nom de la carte dans le tableau ainsi que les indices de bornage
        limits_keys_values = list(limits.values())
        first_key_values = limits_keys_values[0]
        if first_key_values[0]>0:
            limits["NAME"] = [0, first_key_values[0]]
        
        return limits
    
    
    
    def extractDatas(self):
        content_limits = self.getContentLimits()
        page_content = self.page_content
        content_keys = list(content_limits.keys())
        fig_data = {}

        
        for part_name, keys in content_limits.items():
            start_index = keys[0]
            end_index = keys[1]
            for x in range(start_index, end_index):
                content = page_content[x]
                if part_name in ["MELEE WEAPONS", "RANGED WEAPONS"] and self.isDefinition(page_content[x+1]) and x+1<end_index:
                    page_content[x] += page_content[x+1] + ' '
                    page_content[x+1] = ''
                    

                    
                if part_name in ["KEYWORDS", "FACTION KEYWORDS"]:
                    exvar = 0
        stopvar=0
    
    
    
class Figurine:

    def __init__(self, nom):
        self.nom = nom
class PDFFile:
    
    def __init__(self, document):
        self.document = document
    
    def getTotalPage(self):
        return self.document.page_count
    

    
    def extractDataFromPdf(self):
        nb_pages = self.getTotalPage()
        first_horizontale_page = False
        for x_page in range(nb_pages):
            page = PDFPage(self.document.load_page(x_page))
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

 