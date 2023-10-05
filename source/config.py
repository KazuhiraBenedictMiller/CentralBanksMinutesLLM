import os
import sys

from dotenv import load_dotenv

load_dotenv("../.env")

REPLICATE_API_TOKEN = os.environ["REPLICATE_API_TOKEN"]
PINECONE_API_TOKEN = os.environ["PINECONE_API_TOKEN"]

PINECONE_ENVIRONMENT = "gcp-starter"
PINECONE_INDEX_NAME = "centralbanksllm"

LLAMA2_13B = "a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5"