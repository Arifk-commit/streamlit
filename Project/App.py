import streamlit as st
import os
import replicate
import google.generativeai as genai

# App config
st.set_page_config(page_title="🧠 Multi-Model Chatbot", page_icon="🧠")

# Session state init
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
if "model_provider" not in st.session_state:
    st.session_state.model_provider = "🦙💬 LLaMA"

# === Header ===
st.markdown(
    """
    <h1 style='text-align: center;'>🧠 Multi-Model Chatbot</h1>
    <p style='text-align: center; color: gray;'>Choose between 🦙💬 LLaMA or 🤖 Gemini for your AI assistant</p>
    <hr>
    """,
    unsafe_allow_html=True,
)

# Sidebar - Model selection
with st.sidebar:
    st.title("⚙️ Settings")

    # Step 1: Choose Provider
    provider = st.selectbox("Choose a Model Provider", ["🦙💬 LLaMA", "🤖 Gemini"])
    st.session_state.model_provider = provider

    # Step 2: Based on provider, show settings
    if provider == "🦙💬 LLaMA":
        if 'REPLICATE_API_TOKEN' in st.secrets:
            st.success('Replicate API key loaded!', icon='✅')
            replicate_api = st.secrets['REPLICATE_API_TOKEN']
        else:
            replicate_api = st.text_input('Enter Replicate API token:', type='password')
            if not (replicate_api.startswith('r8_') and len(replicate_api) == 40):
                st.warning('Please enter a valid Replicate API token!', icon='⚠️')
            else:
                st.success('API key accepted!', icon='✅')
        os.environ['REPLICATE_API_TOKEN'] = replicate_api

        selected_model = st.selectbox('Choose a LLaMA2 model', ['Llama2-7B', 'Llama2-13B'])
        if selected_model == 'Llama2-7B':
            llm_model = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
        else:
            llm_model = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'

        temperature = st.slider('Temperature', 0.01, 1.0, 0.1, 0.01)
        top_p = st.slider('Top P', 0.01, 1.0, 0.9, 0.01)
        max_length = st.slider('Max Length', 20, 80, 50, 8)

    elif provider == "🤖 Gemini":
        gemini_api = st.text_input("Enter Gemini API key:", type="password")
        if gemini_api:
            try:
                genai.configure(api_key=gemini_api)
                gemini_model = genai.GenerativeModel("gemini-pro")
                st.success("Gemini API key is valid!", icon="✅")
            except Exception as e:
                st.error(f"Gemini API error: {e}")

    st.button("🧹 Clear Chat History", on_click=lambda: st.session_state.update(
        messages=[{"role": "assistant", "content": "How may I assist you today?"}]
    ))

# Display chat history
for msg in st.session_state.messages:
    avatar = "🧑‍💻" if msg["role"] == "user" else ("🦙" if st.session_state.model_provider == "🦙💬 LLaMA" else "🤖")
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

# Function to get response from LLaMA
def get_llama_response(prompt_input):
    dialogue = "You are a helpful assistant.\n"
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        dialogue += f"{'User' if role == 'user' else 'Assistant'}: {content}\n"
    response = replicate.run(llm_model, input={
        "prompt": f"{dialogue}User: {prompt_input}\nAssistant:",
        "temperature": temperature,
        "top_p": top_p,
        "max_length": max_length,
        "repetition_penalty": 1
    })
    return ''.join(response)

# Function to get response from Gemini
def get_gemini_response(prompt_input):
    response = gemini_model.generate_content(prompt_input)
    return response.text

# Input
if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.write(prompt)

    with st.chat_message("assistant", avatar="🦙" if provider == "🦙💬 LLaMA" else "🤖"):
        with st.spinner("Thinking..."):
            try:
                if st.session_state.model_provider == "🦙💬 LLaMA":
                    full_response = get_llama_response(prompt)
                else:
                    full_response = get_gemini_response(prompt)
            except Exception as e:
                full_response = f"❌ Error: {e}"
            st.write(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
