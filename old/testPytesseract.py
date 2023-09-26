import pandas as pd
import numpy as np
import matplotlib as plt
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

image_path = 'D:\\DEV\\Projets\\Github\\WarhadexScanner\\images\\test.png'  # Remplacez 'test_image.png' par le nom de votre image
image = Image.open(image_path)

resultat = pytesseract.image_to_string(image)

print(resultat)
