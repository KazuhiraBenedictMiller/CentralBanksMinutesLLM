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

from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.document_loaders import WebBaseLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain

def CleanTextData(Text):
    
    #Function used to Clean and Preprocess Text Data
    
    #Characters to Replace
    
    ToReplace = {"\n": " ",
                 "\t": " ",
                 "\r": " ",
                 "\xa0": " ",
                 ",": ", ",
                 "  ": " ",
                 "   ": " ",
                 "    ": " ",
                 "     ": " ",
                 "  ": " "  #<- This is Doubled in the Dictionary for a Reason
                }
        
    #Iterating through Dictionary and Cleaning Each Character in Text
        
    for k,v in ToReplace.items():
        Text = [text.replace(k, v) for text in Text]
        
    #Our List contains now a Given Number of Strings, Cleaned by Previous Special Characters
    #First, we Remove Empty and Strings that Contain only one Space
    #Second, we Re-Encode in Latin-1 Encoding in order to be Used by FPDF
    #Third, we Remove Characters not in the Latin-1 Unicode (if not Encoded by Latin-1 they're left with a "?" instead)
        
    Text = [t for t in Text if t != "" and t != " "] 
    Text = [e.encode("latin-1", "replace").decode("latin-1") for e in Text]
    Text = [c.replace("?", "") for c in Text]
        
    return Text

def lower_text(doc):
    doc[0] = doc[0].lower()
    return doc

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
       
        for x in Minutes_Links:
            if x["Link"].endswith(".html"):
                '''
                Loader = WebBaseLoader(RBA_Base_Link + x["Link"])
                d = Loader.load()
            
                #Seps = ["\n", " ", "\t", "\r", "\xa0", ",", ", ", "  ", "   ", "    "]
                #TextSplitter = CharacterTextSplitter(chunk_size = 1000, chunk_overlap = 0, separator = "\n")
                #Text = TextSplitter.split_documents(d)
                
                print(d[0].text)
                break
            '''
                Response = requests.get(RBA_Base_Link + x["Link"])
                Soup = BeautifulSoup(Response.text, "html.parser")

                Div = Soup.find("div", {"id": "content"})

                Text = []

                #for y in Div.find_all("p") -> To get only Paragraphs and not Titles 
                for y in Div:
                    Text.append(y.text)

                CleanedText = CleanTextData(Text)

                CleanedText = "".join(CleanedText)
                TextSplitter = CharacterTextSplitter(chunk_size = 1000, chunk_overlap = 0, separator = " ")    
    

                Splitted = TextSplitter.split_text(CleanedText)
                #print(len(Splitted[0]))
                Embeddings = HuggingFaceEmbeddings() #(model_name = "sentence-transformers/all-MiniLM-L6-v2")
                
                
                
                

        
        StartYear +=1
        
ETL_Pipeline(2006, 2006)