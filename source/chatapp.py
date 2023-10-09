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

def ClearChatHistory():
    st.session_state.messages = [{"role": "Assistant", "content": "Welcome to a Llama 2 LLM Application to Chat with RBA's Monetary Policy Meeting Minutes. \nHow may I assist you today?"}]
    
    st.session_state["ChatHistory"] = []

def Init():
    st.session_state["ChatHistory"] = []
    
    st.session_state["UI_Phase"] = 0

    st.session_state["Init"] = True
    st.session_state["YearsSelected"] = False
    st.session_state["IndexName"] = False

    st.session_state["DataFetched"] = False

    
    st.session_state["StartYear"] = 2006
    st.session_state["EndYear"] = datetime.now().year
    
        
#App title
st.set_page_config(page_title = "🦙💬 Llama 2 Chatbot to Chat with Reserve Bank of Australia's 🏦 Monetary Policy Meeting Minutes")
st.title("🦙💬 Chat with RBA's 🏦 Monetary Policy Meeting Minutes")

if "Init" not in st.session_state.keys() or st.session_state["Init"] != True:
    Init()

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
                st.session_state["YearsSelected"] = True
                st.session_state["UI_Phase"] += 1

if "IndexName" not in st.session_state.keys() or st.session_state["IndexName"] != True:    
    if st.session_state["UI_Phase"] == 1:
        Placeholder = st.empty() 
        Warningg = st.warning("Index Name can only contain Lower Case Letters!!")

        with Placeholder.container():
            Warning = st.warning("Index Name can only contain Lower Case Letters!!")
            IndexName = Placeholder.text_input("Give a Name to the Vector Store Index:")

            if IndexName != "" and IndexName.isalpha() and IndexName.islower():
                Placeholder.empty()
                st.session_state["IndexName"] = True
                st.session_state["UI_Phase"] += 1

        
        
            #Function to Fetch Data, Generate Embeddings and Load them into VectorStore

                


