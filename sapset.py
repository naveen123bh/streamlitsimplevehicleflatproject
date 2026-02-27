import pandas as pd
import streamlit as st
import difflib
from datetime import datetime
import pytz
from streamlit_mic_recorder import mic_recorder
import tempfile
import whisper


# Load Whisper onc
@st.cache_resource
def load_model():
    return whisper.load_model("base")

model = load_model()


def search_and_issue_sets(log_df, LOG_FILE, logged_user):

    df = pd.read_csv("sets.csv", engine="python", on_bad_lines="skip")
    df.columns = ["SetName", "Department", "Floor"]
    df = df.apply(lambda x: x.astype(str).str.upper().str.strip())

    st.subheader("Set Section")

    if "confirmed_set" not in st.session_state:
        st.session_state.confirmed_set = None

    if "similar_set_matches" not in st.session_state:
        st.session_state.similar_set_matches = None

    # -------------------------
    # Search by Set Name
    # -------------------------
    st.markdown("### Search by Set Name")

    col1, col2 = st.columns([4, 1])

    with col1:
        name_input = st.text_input("Enter Set Name", key="set_text")

    with col2:
        audio = mic_recorder(
            start_prompt="🎤",
            stop_prompt="⏹",
            key="set_mic"
        )

    # 🔥 Convert audio → text using Whisper
    if audio is not None:

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            tmpfile.write(audio["bytes"])
            tmp_path = tmpfile.name

        result = model.transcribe(tmp_path)
        spoken_text = result["text"].strip().upper()

        st.session_state["set_text"] = spoken_text
        st.rerun()

    name_input = st.session_state.get("set_text", "").upper().strip()

    if st.button("Search Set"):

        exact = df[df["SetName"] == name_input]

        if not exact.empty:
            st.success("Set Found")
        else:
            st.error("No Set Found")

    return log_df