# ✅ Full updated Streamlit app for KDAH + Instrument Recognition
# programmed by naveen123

import os
import random
import base64
import streamlit as st
import pandas as pd
import difflib
import csv
from datetime import datetime
import pytz
from technician import TECHNICIAN_NAMES
from sapset import search_and_issue_sets
from quotes import get_random_quote

# ---------------------------
# SESSION STATE INIT
# ----------------------------
defaults = {
    "logged_in_user": None,
    "login_selected_name": None,
    "query_option": None,
    "found_pack": None,
    "found_set": None
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -----------------------------
# HELPER FUNCTION
# -----------------------------
def clean_name(name):
    name = name.upper().replace(".", "").replace("!", "").strip()
    for title in ["MR", "MISS"]:
        if name.startswith(title + " "):
            name = name[len(title)+1:]
    return " ".join(name.split())

# -----------------------------
# LOGIN PAGE
# -----------------------------
if st.session_state.logged_in_user is None:

    hospital_image_url = "https://i.ibb.co/7NYqvcHz/hospital.jpg"
    st.image(hospital_image_url, width=400)
    st.markdown("<h2 style='color:purple;'>KDAH</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:green;'>Coded for CSSD Department</h4>", unsafe_allow_html=True)
    st.markdown("<p style='color:orange;'>App is under development</p>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:#444;'>Quote of the Moment</h4>", unsafe_allow_html=True)
    st.info(get_random_quote())

    current_dir = os.path.dirname(os.path.abspath(__file__))
    mp3_files = [os.path.join(current_dir, f) for f in os.listdir(current_dir) if f.lower().endswith(".mp3")]

    if mp3_files:
        random_song = random.choice(mp3_files)
        with open(random_song, "rb") as f:
            audio_bytes = f.read()
        b64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
        <audio>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

    st.markdown("""
    <style>
    div.stButton > button[kind="primary"] {
        background-color: #28a745;
        color: white;
        font-size: 20px;
        font-weight: bold;
        padding: 0.6em 1.2em;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

    name_input = st.text_input("Technician Name")

    if name_input:
        cleaned_input = clean_name(name_input)
        normalized = {clean_name(n): n for n in TECHNICIAN_NAMES}
        if cleaned_input in normalized:
            st.session_state.login_selected_name = normalized[cleaned_input]
        else:
            suggestions = difflib.get_close_matches(cleaned_input, normalized.keys(), n=5, cutoff=0.5)
            if suggestions:
                options = [normalized[s] for s in suggestions]
                st.session_state.login_selected_name = st.selectbox("Did you mean:", options)

    if st.button("Login", type="primary"):
        if st.session_state.login_selected_name:
            st.session_state.logged_in_user = st.session_state.login_selected_name
            st.rerun()
        else:
            st.warning("Enter correct name")

    # -----------------------------
    # Feedback Section (Save to CSV in same folder)
    # -----------------------------
    st.markdown("<h4 style='color:#28a745;'>Suggestions / Feedback (Optional)</h4>", unsafe_allow_html=True)
    feedback_input = st.text_area("Any suggestion or idea to improve this app?")

    if st.button("Submit Suggestion"):
        if feedback_input.strip() != "":
            FEEDBACK_FILE = "cssd_suggestions.csv"
            file_exists = os.path.isfile(FEEDBACK_FILE)

            with open(FEEDBACK_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                if not file_exists:
                    writer.writerow(["DateTime", "Technician", "Feedback"])

                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    st.session_state.login_selected_name or "Unknown",
                    feedback_input
                ])

            st.success("Suggestion saved successfully.")
        else:
            st.warning("Please type something to submit.")

    st.stop()

# -----------------------------
# AFTER LOGIN (rest of your original code continues unchanged)
# -----------------------------