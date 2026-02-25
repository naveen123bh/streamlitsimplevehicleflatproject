#
import streamlit as st

st.title("Instrument Recognition System")

uploaded_file = st.file_uploader("Upload instrument image", type=["jpg","png","jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image")
    st.write("Image received successfully")

from embedding_utils import get_embedding

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image")

    embedding = get_embedding(uploaded_file)
    st.write("Embedding length:", len(embedding))