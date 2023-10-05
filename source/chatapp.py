import os
import shutil
import sys
sys.path.append("../source/")
sys.path.append("../")

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

#App title
st.set_page_config(page_title = "🦙💬 Llama 2 Chatbot to Chat with Reserve Bank of Australia's 🏦 Monetary Policy Meeting Minutes")

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
    
    Temperature = st.sidebar.slider("Temperature", min_value = 0.01, max_value = 5.0, value = 0.1, step = 0.01)
    TopP = st.sidebar.slider("Top P", min_value = 0.01, max_value = 1.0, value = 0.9, step = 0.01)
    MaxLength = st.sidebar.slider('Max Length', min_value= 32, max_value=128, value=120, step = 10)
    st.markdown('📖 Learn how to build this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/)!')
'''
# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function for generating LLaMA2 response. Refactored from https://github.com/a16z-infra/llama2-chatbot
def generate_llama2_response(prompt_input):
    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
    output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', 
                           input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                                  "temperature":temperature, "top_p":top_p, "max_length":max_length, "repetition_penalty":1})
    return output

# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
    
'''