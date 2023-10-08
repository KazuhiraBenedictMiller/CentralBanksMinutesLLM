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

import time
from datetime import datetime

st.session_state["ChatHistory"] = []
st.session_state["Init"] = False
st.session_state["DataFetched"] = False
st.session_state["StartYear"] = 2006
st.session_state["EndYear"] = datetime.now().year

def ClearChatHistory():
    st.session_state.messages = [{"role": "Assistant", "content": "Welcome to a Llama 2 LLM Application to Chat with RBA's Monetary Policy Meeting Minutes. \nHow may I assist you today?"}]
    
    st.session_state["ChatHistory"] = []

def Init():
    with st.spinner("Connecting to the VectorStore"):    
        #Connecting to the VectorStore
        try:
            Warning = st.warning("Connecting to the Vector Store...")

            pinecone.init(api_key = config.PINECONE_API_TOKEN, environment = config.PINECONE_ENVIRONMENT)

        except:
            Warning.empty()

            st.error("Something went wrong with Connecting to the Vectore Database!!")

        finally:
            Warning.empty()

            Success1 = st.success("Connected to the Vector Store!!")    

    with st.spinner("Fetching Data from VectorStore"):
        #Fetching Data from VectorStore
        try:
            Embeddings = HuggingFaceEmbeddings()    

            st.session_state["VectorDB"] = Pinecone.from_existing_index(config.PINECONE_INDEX_NAME, Embeddings)

            Warning = st.warning("Retrieving Vectors from the Vector Store...")

        except:
            Warning.empty()

            st.error("An Error occurred when trying to retreive Data from the Vector Store!!")

        finally:
            Warning.empty()

            Success2 = st.success("Vectors Retrieved from the Store!")

            time.sleep(3)

            Success1.empty()
            Success2.empty()
    
#App title
st.set_page_config(page_title = "🦙💬 Llama 2 Chatbot to Chat with Reserve Bank of Australia's 🏦 Monetary Policy Meeting Minutes")
st.title("🦙💬 Chat with RBA's 🏦 Monetary Policy Meeting Minutes")

if "Init" not in st.session_state.keys() or st.session_state["Init"] != True:
    
    Init()
    
    st.session_state["Init"] = True

if "DataFetched" not in st.session_state.keys() or st.session_state["DataFetched"] != True:
    
    StartYear = st.selectbox(
    "Select the Start Year for the Meeting Minutes to be Fetched:",
    range(2006, st.session_state["EndYear"]+1))
    
    EndYear = st.selectbox(
    "Select the End Year for the Meeting Minutes to be Fetched:",
    range(StartYear, st.session_state["EndYear"]+1))
    
    if st.button("Fetch!"):
        
        #Function to Fetch Data, Generate Embeddings and Load them into VectorStore
        st.text("miao")
        st.empty()

    st.session_state["DataFetched"] = True


