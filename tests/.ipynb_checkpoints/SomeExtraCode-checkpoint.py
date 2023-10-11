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
                

import os
import sys

from dotenv import load_dotenv

load_dotenv("../.env")

PINECONE_API_TOKEN = os.environ["PINECONE_API_TOKEN"]

import pinecone


pinecone.init("njhjh", "gcp-starter")

print("miao")

'''


import requests
from bs4 import BeautifulSoup

import time
from datetime import datetime

        
def ETL_Pipeline(StartYear, EndYear):
    
    # For a Given Range of Years from StartYear to EndYear, we: 
    # 1) Get all the Links for the Minutes
    # 2) Scrape the Content
    # 3) Clean the Data 
    # 4) Generate Embeddings
    # 5) Load Embeddings into the Vector Store
    
    RBA_Base_Link = "https://www.rba.gov.au/"
    Monetary_Policy_Link = "monetary-policy/rba-board-minutes/"
    
    while StartYear <= EndYear:
        
        # 1) Getting all the Links
        Complete_Link = RBA_Base_Link + Monetary_Policy_Link + str(StartYear) + "/"
    
        Response = requests.get(Complete_Link)
        Soup = BeautifulSoup(Response.text,"html.parser")

        UL = Soup.find("ul", {"class": "list-articles"})
        As = UL.find_all("a")
        Minutes_Links = [{"Link" : x["href"], "Title" : x.text.replace(" ", "_")} for x in As]
        
        print(Minutes_Links)
        
        StartYear +=1
        
ETL_Pipeline(2006, 2006)