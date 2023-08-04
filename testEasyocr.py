import easyocr
import cv2
import pandas as pd
reader = easyocr.Reader(['en'], gpu=True)
result = reader.readtext('D:\\DEV\\Projets\\Github\\WarhadexScanner\\images\\test.png', detail = 0)
print(pd.DataFrame(result))