import os
import shutil
import sys
sys.path.append("../source/")
sys.path.append("../")

import paths
import config
import webscraper

from dotenv import load_dotenv

load_dotenv("../.env")

import pinecone
from langchain.llms import Replicate
from langchain.vectorstores import Pinecone
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import HuggingFaceEmbeddings

def LoadToVectorStore(Text, Embeddings, IndexName):
    
    pinecone.init(api_key = config.PINECONE_API_TOKEN, environment = config.PINECONE_ENVIRONMENT)

    Index = pinecone.Index(config.PINECONE_INDEX_NAME)
    VectorDB = Pinecone.from_documents(Text, Embeddings, index_name = config.PINECONE_INDEX_NAME)

def ETL_Pipeline(StartYear, EndYear):
    
    webscraper.ScrapeData(StartYear, EndYear)
    
    for x in os.listdir(paths.TRANSFORMED_DATA_DIR):
        if x.endswith(".pdf"):
            
            FilePath = str(paths.TRANSFORMED_DATA_DIR / x)
            Loader = PyPDFLoader(FilePath)
            Document = Loader.load()
        
            TextSplitter = CharacterTextSplitter(chunk_size = 1000, chunk_overlap = 0)
            Text = TextSplitter.split_documents(Document)
            Embeddings = HuggingFaceEmbeddings() #(model_name = "sentence-transformers/all-MiniLM-L6-v2")
        
            #Loading Documents into the Vector Database

            LoadToVectorStore(Text, Embeddings, config.PINECONE_INDEX_NAME)
        
            #After Loading the Documents' Embeddings to the Vector Store, the File is Moved to a Storage Directory

            shutil.move(FilePath, str(paths.STORAGE_DATA_DIR / x))