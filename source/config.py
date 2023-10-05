import os
import sys

from dotenv imp
load_dotenv("../.env")

REPLICATE_API_TOKEN = os.environ["REPLICATE_API_TOKEN"]
PINECONE_API_TOKEN = os.environ["PINECONE_API_TOKEN"]

PINECONE_ENVIRONMENT = "gcp-starter"
PINECONE_INDEX_NAME = "centralbanksllm"