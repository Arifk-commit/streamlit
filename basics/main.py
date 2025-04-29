import streamlit as st

st.title("Hello Programers")
st.text("This is a basic app")
st.write("choose your prefered language")
lang =st.selectbox("Languages : " , ["CPP" ,"Java" ,"Python"])
st.success(f"{lang} is a great choice")
