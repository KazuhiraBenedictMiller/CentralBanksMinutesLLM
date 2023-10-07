import os
import shutil
import sys
sys.path.append("../source/")
sys.path.append("../")

from dotenv import load_dotenv

load_dotenv("../.env")

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

from datetime import datetime

#App title
st.set_page_config(page_title = "🦙💬 Llama 2 Chatbot to Chat with Reserve Bank of Australia's 🏦 Monetary Policy Meeting Minutes")
st.title("🦙💬 Chat with RBA's 🏦 Monetary Policy Meeting Minutes")

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
    
    LLM = config.LLAMA2_13B
    
    Temperature = st.sidebar.slider("Temperature", min_value = 0.01, max_value = 5.0, value = 0.75, step = 0.01)
    TopP = st.sidebar.slider("Top P", min_value = 0.01, max_value = 1.0, value = 0.75, step = 0.01)
    MaxLength = st.sidebar.slider('Max Length', min_value = 10, max_value = 5000, value = 3000, step = 10)
    
    StartYear = st.selectbox(
    "Select the Start Year for the Meeting Minutes to be Fetched:",
    range(2006, datetime.now().year+1))
    
    EndYear = st.selectbox(
    "Select the End Year for the Meeting Minutes to be Fetched:",
    range(StartYear, datetime.now().year+1))
    
    st.markdown('📖 Learn how to build this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/)!')

#Connecting to the VectorStore
try:
    pinecone.init(api_key = config.PINECONE_API_TOKEN, environment = config.PINECONE_ENVIRONMENT)
    
except:
    st.error("Something went wrong with Connecting to the Vectore Database!!")
    
else:
    st.success("Connected to the Vector Store!!")    

finally:
    
    try:
    Embeddings = HuggingFaceEmbeddings()    

    VectorDB = Pinecone.from_existing_index(config.PINECONE_INDEX_NAME, Embeddings)
    
    Warning = st.warning("Retrieving Vectors from the Vector Store...")
    
    x+x
    
    except:
        
        Warning.empty()
    
        st.error("An Error occurred when trying to retreive Data from the Vector Store!!")
    
