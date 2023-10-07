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
import replicate

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
    
    Temperature = st.sidebar.slider("Temperature", min_value = 0.01, max_value = 5.0, value = 0.75, step = 0.01)
    TopP = st.sidebar.slider("Top P", min_value = 0.01, max_value = 1.0, value = 0.75, step = 0.01)
    MaxLength = st.sidebar.slider('Max Length', min_value = 10, max_value = 5000, value = 3000, step = 10)
    
    st.markdown('📖 Learn how to build this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/)!')

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "Assistant", "content": "Welcome to a Llama 2 LLM Application to Chat with RBA's Monetary Policy Meeting Minutes. \nHow may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "Assistant", "content": "Welcome to a Llama 2 LLM Application to Chat with RBA's Monetary Policy Meeting Minutes. \nHow may I assist you today?"}]
    
st.sidebar.button("Clear Chat History", on_click = clear_chat_history)

# Function for generating LLaMA2 response. Refactored from https://github.com/a16z-infra/llama2-chatbot
def generate_llama2_response(PromptInput):
    
    StringDialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    
    for dict_message in st.session_state.messages:
        
        if dict_message["role"] == "User":
            
            StringDialogue += "User: " + dict_message["content"] + "\n\n"
            
        else:
            
            StringDialogue += "Assistant: " + dict_message["content"] + "\n\n"
            
    output = replicate.run(config.LLAMA2_13B, 
                           input={"prompt": f"{StringDialogue} {PromptInput} Assistant: ",
                                  "temperature": Temperature, "top_p": TopP, "max_length": MaxLength, "repetition_penalty": 1})
    return output

# User-provided prompt
if Prompt := st.chat_input(disabled = not Replicate_API):
    
    st.session_state.messages.append({"role": "User", "content": Prompt})
    
    with st.chat_message("User"):
        
        st.write(Prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "Assistant":
    
    with st.chat_message("Assistant"):
        
        with st.spinner("Thinking..."):
            
            Response = generate_llama2_response(Prompt)
            Placeholder = st.empty()
            FullResponse = ''
            
            for item in Response:
                
                FullResponse += item
                Placeholder.markdown(FullResponse)
                
            Placeholder.markdown(FullResponse)
            
    Message = {"role": "assistant", "content": FullResponse}
    
    st.session_state.messages.append(Message)
