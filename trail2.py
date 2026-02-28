# ✅ Full updated Streamlit app for KDAH + Instrument Recognition
# programmed by naveen123

import os
import random
import base64
import streamlit as st
import pandas as pd
import difflib
import urllib.parse
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
    # Feedback Section (Send to WhatsApp)
    # -----------------------------
    st.markdown("<h4 style='color:#28a745;'>Suggestions / Feedback (Optional)</h4>", unsafe_allow_html=True)
    feedback_input = st.text_area("Any suggestion or idea to improve this app?")

    if st.button("Send via WhatsApp"):
        if feedback_input.strip() != "":
            
            phone_number = "917247889502"

            message = f"""
New Suggestion:
Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Technician: {st.session_state.login_selected_name or "Unknown"}
Suggestion: {feedback_input}
            """

            encoded_message = urllib.parse.quote(message)
            whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_message}"

            st.markdown(f"[Click Here to Send Suggestion on WhatsApp]({whatsapp_url})")
        else:
            st.warning("Please type something to submit.")

    st.stop()