import streamlit as st
import replicate
import os
import google.generativeai as genai

# Page setup
st.set_page_config(page_title="🧠 Multi-Model Chatbot")

# Sidebar - Model selection
with st.sidebar:
    st.title("🤖🦙 Multi-Model Chatbot")
    
    model_provider = st.radio("Choose Model Provider", ["🦙 LLaMA", "🤖 Gemini"])
    
    if model_provider == "🦙 LLaMA":
        # Replicate credentials
        if 'REPLICATE_API_TOKEN' in st.secrets:
            st.success('Replicate API token found ✅')
            replicate_api = st.secrets['REPLICATE_API_TOKEN']
        else:
            replicate_api = st.text_input("Enter Replicate API token:", type="password")
            if replicate_api.startswith('r8_') and len(replicate_api) == 40:
                st.success("Token format looks good ✅")
            else:
                st.warning("Enter a valid Replicate token")
        os.environ["REPLICATE_API_TOKEN"] = replicate_api

        selected_model = st.selectbox("Choose LLaMA Model", ['Llama2-7B', 'Llama2-13B'])
        if selected_model == 'Llama2-7B':
            llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
        else:
            llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'
        temperature = st.slider("Temperature", 0.01, 1.0, 0.1, 0.01)
        top_p = st.slider("Top-p", 0.01, 1.0, 0.9, 0.01)
        max_length = st.slider("Max Length", 20, 80, 30, 8)

    else:
        # Google Gemini API Key
        google_api_key = st.text_input("Enter Google API Key:", type="password")
        if google_api_key:
            genai.configure(api_key=google_api_key)
            gemini_model = st.selectbox("Gemini Model", [
                "models/gemini-1.5-pro-latest",
                "models/gemini-1.0-pro"
            ])
            st.success("Google Gemini configured ✅")
        else:
            st.warning("Enter a valid Google API key")


# Chat session state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How can I help you today?"}]

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Clear chat button
def clear_chat():
    st.session_state.messages = [{"role": "assistant", "content": "How can I help you today?"}]
st.sidebar.button("🧹 Clear Chat", on_click=clear_chat)

# LLaMA response generator
def generate_llama_response(prompt):
    history = ""
    for m in st.session_state.messages:
        if m["role"] == "user":
            history += f"User: {m['content']}\n"
        else:
            history += f"Assistant: {m['content']}\n"
    full_prompt = f"{history}User: {prompt}\nAssistant:"
    output = replicate.run(llm, input={
        "prompt": full_prompt,
        "temperature": temperature,
        "top_p": top_p,
        "max_length": max_length,
        "repetition_penalty": 1
    })
    return "".join(output)

# Gemini response generator
def generate_gemini_response(prompt):
    model = genai.GenerativeModel(gemini_model)
    response = model.generate_content(prompt)
    return response.text

# Chat input
if prompt := st.chat_input("Say something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if model_provider == "🦙 LLaMA":
                answer = generate_llama_response(prompt)
            else:
                answer = generate_gemini_response(prompt)
            st.write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
