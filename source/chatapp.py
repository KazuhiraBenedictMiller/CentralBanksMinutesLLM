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
from langchain.text_splitter import CharacterTextSplitter
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

        #UL = Soup.find("ul", {"class": "list-articles"})
        #As = UL.find_all("a") <- Not Working on Streamlit for Unknown Reasons
        As = Soup.select("ul[class=list-articles] > li > a")
                
        Minutes_Links = [{"Link" : x["href"], "Title" : x.text.replace(" ", "_")} for x in As]

        # 2) Scrape the Content
        for x in Minutes_Links:
            if x["Link"].endswith("html"):
                Response = requests.get(RBA_Base_Link + x["Link"])
                Soup = BeautifulSoup(Response.text, "html.parser")

                Div = Soup.find("div", {"id": "content"})

                Text = []

                #for y in Div.find_all("p") -> To get only Paragraphs and not Titles 
                for y in Div:
                    Text.append(y.text)
                
                # 3) Cleaning Data
                CleanedText = CleanTextData(Text)
                CleanedText = "".join(CleanedText)
                TextSplitter = CharacterTextSplitter(chunk_size = 1000, chunk_overlap = 0, separator = " ")    
                SplittedText = TextSplitter.split_text(CleanedText)
                #print(len(Splitted[0]))
                
                # 4) Embeddings
                Embeddings = HuggingFaceEmbeddings() #(model_name = "sentence-transformers/all-MiniLM-L6-v2")
                
                # 5) Loading Documents into the Vector Database
                #LoadToVectorStore(SplittedText, Embeddings, st.session_state["VectorDBIndexName"])
                VectorDB = Pinecone.from_texts(SplittedText, Embeddings, index_name = st.session_state["VectorDBIndexName"])

        StartYear += 1

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
    st.session_state["RetrievingPhase"] = False
    st.session_state["ModelPhase"] = False
    st.session_state["ChatPhase"] = False
    
    st.session_state["VectorDBIndexName"] = ""
    st.session_state["VectorDB"] = ""
    st.session_state["LLM"] = ""
    
    st.session_state["StartYearRange"] = 2006
    st.session_state["EndYearRange"] = datetime.now().year
    
    st.session_state["StartYear"] = 2006
    st.session_state["EndYear"] = 2006
        
def BuildModel(Model, Params):
    LLM = Replicate(model = Model, model_kwargs = Params)
    
    return LLM
    
    
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
            range(st.session_state["StartYearRange"], st.session_state["EndYearRange"]+1))

            EndYear = st.selectbox(
            "Select the End Year for the Meeting Minutes to be Fetched:",
            range(StartYear, st.session_state["EndYearRange"]+1))

            if st.button("Fetch!"):
                st.session_state["StartYear"] = int(StartYear)
                st.session_state["EndYear"] = int(EndYear)
                st.session_state["YearsSelected"] = True
                
                st.session_state["UI_Phase"] += 1
                Placeholder.empty()

#Naming the Index in the Vector Store
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
        
        ProgressBar = st.progress(0, "Progress")
        
        with st.spinner("Connecting to the VectorStore"):
            #Connecting to the VectorStore
            pinecone.init(api_key = config.PINECONE_API_TOKEN, environment = config.PINECONE_ENVIRONMENT)
            ProgressBar.progress(33)
        
        with st.spinner("Creating the Vector Index"):
            pinecone.create_index(st.session_state["VectorDBIndexName"], dimension=768)
            ProgressBar.progress(66)
        
        #st.text(type(st.session_state["StartYear"]))
        #st.text(st.session_state["StartYear"])
        #st.text(type(st.session_state["EndYear"]))
        #st.text(st.session_state["EndYear"])
        
        with st.spinner("Fetching Data"):
            #Function to Fetch Data, Generate Embeddings and Load them into VectorStore
            ETL_Pipeline(int(st.session_state["StartYear"]), int(st.session_state["EndYear"]))
            ProgressBar.progress(100)
        
        st.session_state["FetchingPhase"] = True
        st.session_state["UI_Phase"] += 1
        ProgressBar.empty()

#Retrieving the Data from the Vector Store
if "RetrievingPhase" not in st.session_state.keys() or st.session_state["RetrievingPhase"] != True:    
    with st.spinner("Retrieving Data from the Vector Store"):
        pinecone.init(api_key = config.PINECONE_API_TOKEN, environment = config.PINECONE_ENVIRONMENT)
        
        Embeddings = HuggingFaceEmbeddings()
        st.session_state["VectorDB"] = Pinecone.from_existing_index(st.session_state["VectorDBIndexName"], Embeddings)
        
        st.session_state["RetrievingPhase"] = True
                
#Building the LLM
if "ModelPhase" not in st.session_state.keys() or st.session_state["ModelPhase"] != True:    
    with st.spinner("Building the LLM Model"):
        st.session_state["LLM"] = BuildModel(config.LLAMA2_13B, {"temperature":Temperature, "top_p":TopP, "max_length":MaxLength})
        
        st.session_state["LLM"] = True
        
#Chatting Time
if "ChatPhase" not in st.session_state.keys() or st.session_state["ChatPhase"] != True:    
    if st.session_state["UI_Phase"] == 3:
        
        #Sidebar
        #Replicate Credentials
        with st.sidebar:
            st.title("🦙💬 Llama 2 RBA Meeting Minutes Chatbot")

            if 'REPLICATE_API_TOKEN' in st.secrets:

                st.success("Replicate API Token has been provided!", icon='✅')
                Replicate_API = st.secrets['REPLICATE_API_TOKEN']

            else:

                Replicate_API = st.text_input("Replicate API_TOKEN not found, Please Enter Replicate API token:", type = "password")

                if not (Replicate_API.startswith('r8_') and len(Replicate_API) == 40):

                    st.warning("Wrong Replicate API Token, Please enter your credentials!", icon = "⚠️")

                else:

                    st.success("Done, Proceed to entering your prompt message!", icon = "👉")

            os.environ['REPLICATE_API_TOKEN'] = Replicate_API
            
            st.subheader("Adjust Parameters to your Needs 👇")
            
            Temperature = st.sidebar.slider("Temperature - Higher -> More Creative", min_value = 0.01, max_value = 5.0, value = 0.75, step = 0.01)
            TopP = st.sidebar.slider("Top P - Higher -> More Different Words Used", min_value = 0.01, max_value = 1.0, value = 0.75, step = 0.01)
            MaxLength = st.sidebar.slider('Max Length', min_value = 10, max_value = 5000, value = 3000, step = 10)
                        
            st.sidebar.button("Modify Model Parameters", on_click = BuildModel(config.LLAMA2_13B, {"temperature":Temperature, "top_p":TopP, "max_length":MaxLength}))
            st.sidebar.button("Clear Chat History", on_click = ClearChatHistory)
            
            st.markdown('📖 Learn how to build this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/)!')

            #Store LLM generated responses
        if "messages" not in st.session_state.keys():
            st.session_state.messages = [{"role": "Assistant", "content": "Welcome to a Llama 2 LLM Application to Chat with RBA's Monetary Policy Meeting Minutes. \nHow may I assist you today?"}]

            
        #Display or clear chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        QA_Chain = ConversationalRetrievalChain.from_llm(st.session_state["LLM"], st.session_state["VectorDB"].as_retriever(search_kwargs = {"k": 2}), return_source_documents = True)    

        PromptTemplate = "You are one of the best Financial Analyst in the World, if you don't know an answer simply say that you don't know and don't try to make it up."

        # User-provided prompt
        if Prompt := st.chat_input(disabled = not Replicate_API):

            st.session_state.messages.append({"role": "User", "content": Prompt})

            with st.chat_message("User"):

                st.write(Prompt)

            LLMPrompt = PromptTemplate + Prompt

        # Generate a new response if last message is not from assistant
        if st.session_state.messages[-1]["role"] != "Assistant":

            with st.chat_message("Assistant"):

                with st.spinner("Thinking..."):

                    Result = QA_Chain({'question': LLMPrompt, 'chat_history': st.session_state["ChatHistory"]})
                    Response = Result['answer']
                    Placeholder = st.empty()
                    FullResponse = ""

                    for item in Response:

                        FullResponse += item
                        Placeholder.markdown(FullResponse)

                    Placeholder.markdown(FullResponse)

                Message = {"role": "Assistant", "content": FullResponse}

                st.session_state.messages.append(Message)
                st.session_state["ChatHistory"].append((LLMPrompt, Result['answer']))

        #st.session_state["ChatPhase"] = True
        #st.session_state["UI_Phase"] += 1
        