import os
import shutil
import sys
sys.path.append("../source/")
sys.path.append("../")

from dotenv import load_dotenv

load_dotenv("../.env")

import pinecone
from langchain.llms import Replicate
from langchain.vectorstores import Pinecone
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.chains import RetrievalQAWithSourcesChain

import streamlit as st
import langchain
import replicate

def Init():
    st.session_state["UI_Phase"] = 0
    st.session_state["Init"] = True

def AdvancePhase():
    st.session_state["UI_Phase"] += 1
    
st.set_page_config(layout = "centered", page_title = "Chat with 1 or More PDFs")
st.header("Multidoc QnA")

#Initialization
if "Init" not in st.session_state.keys() or st.session_state["Init"] != True:
    Init()

if st.session_state["UI_Phase"] == 0:   
    #Placeholder = st.empty() 

    with st.empty():
        #File Uploader
        UploadedFiles = st.file_uploader("Upload your Documents in .pdf Format" , accept_multiple_files = True, type = ["pdf"])

        if UploadedFiles is None:
            st.info("Upload Files to Chat With")

        elif UploadedFiles:
            st.write(str(len(UploadedFiles)) + " Document(s) Loaded")

        st.button("Chat!", on_click = AdvancePhase)

if st.session_state["UI_Phase"] == 1:    
    for x in UploadedFiles:
        Loader = PyPDFLoader(x)
        Document = Loader.load()
        
        TextSplitter = CharacterTextSplitter(chunk_size = 1000, chunk_overlap = 0)
        Text = TextSplitter.split_documents(Document)
        Embeddings = HuggingFaceEmbeddings() #(model_name = "sentence-transformers/all-MiniLM-L6-v2")
        
        #Loading Documents into the Vector Database
        IndexName = "pdfsllm"
        Index = pinecone.Index(IndexName)
        VectorDB = Pinecone.from_documents(Text, Embeddings, index_name = IndexName)

        
        
'''

#file uploader
uploaded_files = st.file_uploader("Upload documents",accept_multiple_files=True, type=["txt","pdf"])
st.write("---")

if uploaded_files is None:
  st.info(f"""Upload files to analyse""")
elif uploaded_files:
  st.write(str(len(uploaded_files)) + " document(s) loaded..")
  
  textify_output = read_and_textify(uploaded_files)
  
  documents = textify_output[0]
  sources = textify_output[1]
  
  #extract embeddings
  embeddings = OpenAIEmbeddings(openai_api_key = st.secrets["openai_api_key"])
  #vstore with metadata. Here we will store page numbers.
  vStore = Chroma.from_texts(documents, embeddings, metadatas=[{"source": s} for s in sources])
  #deciding model
  model_name = "gpt-3.5-turbo"
  # model_name = "gpt-4"

  retriever = vStore.as_retriever()
  retriever.search_kwargs = {'k':2}

  #initiate model
  llm = OpenAI(model_name=model_name, openai_api_key = st.secrets["openai_api_key"], streaming=True)
  model = RetrievalQAWithSourcesChain.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)
  
  st.header("Ask your data")
  user_q = st.text_area("Enter your questions here")
  
  if st.button("Get Response"):
    try:
      with st.spinner("Model is working on it..."):
        result = model({"question":user_q}, return_only_outputs=True)
        st.subheader('Your response:')
        st.write(result['answer'])
        st.subheader('Source pages:')
        st.write(result['sources'])
    except Exception as e:
      st.error(f"An error occurred: {e}")
      st.error('Oops, the GPT response resulted in an error :( Please try again with a different question.')
      
        
    
  
  
  
  
  
  
  
  
  
'''