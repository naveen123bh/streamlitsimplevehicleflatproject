import streamlit as st
from embedding_utils import get_embedding

st.set_page_config(page_title="Instrument Recognition System")

st.title("Instrument Recognition System")

uploaded_file = st.file_uploader(
    "Upload instrument image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    st.success("Image received successfully")

    try:
        embedding = get_embedding(uploaded_file)

        st.write("Shape:", embedding.shape)
        st.write("Embedding length:", len(embedding))

    except Exception as e:
        st.error("Error generating embedding")
        st.write(str(e))