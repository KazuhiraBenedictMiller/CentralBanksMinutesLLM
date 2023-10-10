'''
from bs4 import BeautifulSoup
import requests

from fpdf import FPDF

import os
import sys
sys.path.append("../source/")
sys.path.append("../")

import paths

def FetchDataForYear(Links):
    
    for x in Links:
        
        RBA_Base_Link = "https://www.rba.gov.au/"

        Response = requests.get(RBA_Base_Link + x["Link"])
        Soup = BeautifulSoup(Response.text,"html.parser")

        Div = Soup.find("div", {"id": "content"})

        T = []

        for y in Div:
            T.append(y.text)

        Text = [text.replace("\n", "").replace("\t", "").replace("\xa0", " ").replace(",", ", ").replace("  ", " ") for text in T]
        Text = [t for t in Text if t != ""] 

        File_Path = paths.TRANSFORMED_DATA_DIR / f'{x["Title"]}.txt'

        if not File_Path.exists():
            with open (File_Path, "w", encoding = "utf-8") as f:
                f.write('\n'.join(Text))
                
'''

import os
import sys

from dotenv import load_dotenv

load_dotenv("../.env")

PINECONE_API_TOKEN = os.environ["PINECONE_API_TOKEN"]

import pinecone


pinecone.init("njhjh", "gcp-starter")

print("miao")