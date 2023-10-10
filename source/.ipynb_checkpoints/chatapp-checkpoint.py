import os
import shutil
import sys
sys.path.append("../source/")
sys.path.append("../")

from dotenv import load_dotenv

load_dotenv("../.env")

import requests
from bs4 import BeautifulSoup

import paths
import config
import webscraper
import etlpipeline

import pinecone
from langchain.llms import Replicate
from langchain.vectorstores import Pinecone
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain

import streamlit as st
import replicate

import time
from datetime import datetime

def CleanTextData(Text):
    
    #Function used to Clean and Preprocess Text Data
    
    #Characters to Replace
    
    ToReplace = {"\n": " ",
                 "\t": " ",
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

def PrintPDF(File_Path, Title, CleanedText):
    
    #Function Only used to Dump the PDF to Disk
    
    #If File doesn't Exist, it then sets the pdf properties and it dumps to Disk
    
    if not File_Path.exists():
        PDF = FPDF()
        PDF.add_page()
        PDF.set_font("Arial", size = 10)
        PDF.set_margins(left = 10, top = 10, right = 10)
            
        for text in CleanedText:
            PDF.multi_cell(w = 0, h = 9, txt = text, align = "L")

        PDF.output(File_Path)
    
    else:
        print(f'{Title} Already Processed and in the Vector Store. Check in the Storage Directory.')
        
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

        # 2) Scrape the Content
        for x in Minutes_Links:
            if x.endswith("html"):
                Response = requests.get(RBA_Base_Link + x["Link"])
                Soup = BeautifulSoup(Response.text, "html.parser")

                Div = Soup.find("div", {"id": "content"})

                Text = []

                #for y in Div.find_all("p") -> To get only Paragraphs and not Titles 
                for y in Div:
                    Text.append(y.text)
                
                # 3) Cleaning Data
                CleanedText = CleanTextData(Text)

                PrintPDF(paths.STORAGE_DATA_DIR / f'{x["Title"]}.pdf', f'{x["Title"]}.pdf', CleanedText)

        StartYear += 1
        
    for z in os.listdir(paths.TRANSFORMED_DATA_DIR):
        if z.endswith(".pdf"):
            
            FilePath = str(paths.TRANSFORMED_DATA_DIR / z)
            Loader = PyPDFLoader(FilePath)
            Document = Loader.load()
        
            TextSplitter = CharacterTextSplitter(chunk_size = 1000, chunk_overlap = 0)
            Text = TextSplitter.split_documents(Document)
            
            # 4) Generate Embeddings
            Embeddings = HuggingFaceEmbeddings() #(model_name = "sentence-transformers/all-MiniLM-L6-v2")
        
            # 5) Loading Documents into the Vector Database

            LoadToVectorStore(Text, Embeddings, st.session_state["VectorDBIndexName"])
        
            #After Loading the Documents' Embeddings to the Vector Store, the File is Moved to a Storage Directory

            shutil.move(FilePath, str(paths.STORAGE_DATA_DIR / z))

    
def ClearChatHistory():
    st.session_state.messages = [{"role": "Assistant", "content": "Welcome to a Llama 2 LLM Application to Chat with RBA's Monetary Policy Meeting Minutes. \nHow may I assist you today?"}]
    
    st.session_state["ChatHistory"] = []

def Init():
    st.session_state["ChatHistory"] = []
    
    st.session_state["UI_Phase"] = 0

    st.session_state["Init"] = True
    st.session_state["YearsSelected"] = False
    st.session_state["IndexName"] = False
    st.session_state["FetchingPhase"] = False
    
    st.session_state["VectorDBIndexName"] = ""
    
    st.session_state["StartYearRange"] = 2006
    st.session_state["EndYearRange"] = datetime.now().year
    
    st.session_state["StartYear"] = 0
    st.session_state["EndYear"] = 0
        
#App title
st.set_page_config(page_title = "🦙💬 Llama 2 Chatbot to Chat with Reserve Bank of Australia's 🏦 Monetary Policy Meeting Minutes")
st.title("🦙💬 Chat with RBA's 🏦 Monetary Policy Meeting Minutes")

#Initialization
if "Init" not in st.session_state.keys() or st.session_state["Init"] != True:
    Init()

#Selecting Years or the Data to be Fetched
if "YearsSelected" not in st.session_state.keys() or st.session_state["YearsSelected"] != True:
    if st.session_state["UI_Phase"] == 0:
        Placeholder = st.empty() 

        with Placeholder.container():      
            StartYear = st.selectbox(
            "Select the Start Year for the Meeting Minutes to be Fetched:",
            range(2006, st.session_state["EndYear"]+1))

            EndYear = st.selectbox(
            "Select the End Year for the Meeting Minutes to be Fetched:",
            range(StartYear, st.session_state["EndYear"]+1))

            if st.button("Fetch!"):
                Placeholder.empty()
                
                st.session_state["StartYear"] = StartYear
                st.session_state["EndYear"] = EndYear
                st.session_state["YearsSelected"] = True
                st.session_state["UI_Phase"] += 1

#Naming the Index in the Feature Store
if "IndexName" not in st.session_state.keys() or st.session_state["IndexName"] != True:    
    if st.session_state["UI_Phase"] == 1:
        Placeholder = st.empty() 
        Warning = st.warning("Index Name can only contain Lower Case Letters!!")

        with Placeholder.container():
            IndexName = Placeholder.text_input("Give a Name to the Vector Store Index:")
            st.session_state["VectorDBIndexName"] = IndexName
            
            if IndexName != "" and IndexName.isalpha() and IndexName.islower():
                Placeholder.empty()
                Warning.empty()
                st.session_state["IndexName"] = True
                st.session_state["UI_Phase"] += 1

#Actually Fetching the Data
if "FetchingPhase" not in st.session_state.keys() or st.session_state["FetchingPhase"] != True:    
    if st.session_state["UI_Phase"] == 2:
        
        ProgressBar = st.progress(0, "Connecting to the VectorStore")
        
        #Connecting to the VectorStore
        pinecone.init(api_key = config.PINECONE_API_TOKEN, environment = config.PINECONE_ENVIRONMENT)

        ProgressBar = st.progress(10, "Creating the Vector Index")
        
        pinecone.create_index(st.session_state["VectorDBIndexName"], dimension=768)
        
        ProgressBar.progress(20, "Fetching Data")
        
        ETL_Pipeline(st.session_state["StartYear"], st.session_state["EndYear"])
        
        #Function to Fetch Data, Generate Embeddings and Load them into VectorStore

                


