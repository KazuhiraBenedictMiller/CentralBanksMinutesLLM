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

global ChatHistory
ChatHistory =[]

def ClearChatHistory():
    st.session_state.messages = [{"role": "Assistant", "content": "Welcome to a Llama 2 LLM Application to Chat with RBA's Monetary Policy Meeting Minutes. \nHow may I assist you today?"}]
    
    ChatHistory = []


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
    
    Temperature = st.sidebar.slider("Temperature - Higher -> More Creative", min_value = 0.01, max_value = 5.0, value = 0.75, step = 0.01)
    TopP = st.sidebar.slider("Top P - Higher -> More Different Words Used", min_value = 0.01, max_value = 1.0, value = 0.75, step = 0.01)
    MaxLength = st.sidebar.slider('Max Length', min_value = 10, max_value = 5000, value = 3000, step = 10)
    
    StartYear = st.selectbox(
    "Select the Start Year for the Meeting Minutes to be Fetched:",
    range(2006, datetime.now().year+1))
    
    EndYear = st.selectbox(
    "Select the End Year for the Meeting Minutes to be Fetched:",
    range(StartYear, datetime.now().year+1))
    
    st.sidebar.button("Clear Chat History", on_click = ClearChatHistory)
    
    st.markdown('📖 Learn how to build this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/)!')
    
#Connecting to the VectorStore
try:
    Warning = st.warning("Connecting to the Vector Store...")
    
    pinecone.init(api_key = config.PINECONE_API_TOKEN, environment = config.PINECONE_ENVIRONMENT)
    
except:
    Warning.empty()
    
    st.error("Something went wrong with Connecting to the Vectore Database!!")
    
else:
    Warning.empty()
    
    Success1 = st.success("Connected to the Vector Store!!")    

finally:
    
    try:
        Embeddings = HuggingFaceEmbeddings()    

        VectorDB = Pinecone.from_existing_index(config.PINECONE_INDEX_NAME, Embeddings)
    
        Warning = st.warning("Retrieving Vectors from the Vector Store...")
    
    except:
        Warning.empty()
    
        st.error("An Error occurred when trying to retreive Data from the Vector Store!!")

    else:
        Warning.empty()
        
        Success2 = st.success("Vectors Retrieved from the Store!")
        
        time.sleep(3)
        
        Success1.empty()
        Success2.empty()
        
    finally:
        #Store LLM generated responses
        if "messages" not in st.session_state.keys():
            st.session_state.messages = [{"role": "Assistant", "content": "Welcome to a Llama 2 LLM Application to Chat with RBA's Monetary Policy Meeting Minutes. \nHow may I assist you today?"}]

        #Display or clear chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
        LLM = Replicate(model = config.LLAMA2_13B, model_kwargs = {"temperature": Temperature, "top_p": TopP, "max_length": MaxLength})
                
        QA_Chain = ConversationalRetrievalChain.from_llm(LLM, VectorDB.as_retriever(search_kwargs = {"k": 2}), return_source_documents = True)    
    
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
                    
                    Result = QA_Chain({'question': LLMPrompt, 'chat_history': ChatHistory})
                    Response = Result['answer']
                    Placeholder = st.empty()
                    FullResponse = ""

                    for item in Response:

                        FullResponse += item
                        Placeholder.markdown(FullResponse)

                    Placeholder.markdown(FullResponse)

            Message = {"role": "Assistant", "content": FullResponse}

            st.session_state.messages.append(Message)
            ChatHistory.append((LLMPrompt, Result['answer']))