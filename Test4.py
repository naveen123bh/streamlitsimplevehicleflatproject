# app.py
# ✅ Full updated Streamlit app for KDAH + Instrument Recognition
# programmed by naveen123

import os
import random
import base64
import streamlit as st
import pandas as pd
import difflib
from datetime import datetime
import pytz
from technician import TECHNICIAN_NAMES
from sapset import search_and_issue_sets
from quotes import get_random_quote

# -----------------------------
# SESSION STATE INIT
# -----------------------------
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

    # Feedback Section
    st.markdown("<h4 style='color:#28a745;'>Suggestions / Feedback (Optional)</h4>", unsafe_allow_html=True)
    feedback_input = st.text_area("Any suggestion or idea to improve this app?")
    if st.button("Submit Suggestion"):
        if feedback_input.strip() != "":
            FEEDBACK_FILE = "cssd_suggestions.csv"
            import csv
            with open(FEEDBACK_FILE, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                 st.session_state.login_selected_name or "Unknown",
                                 feedback_input])
            st.success("Thank you! Your suggestion has been recorded.")
        else:
            st.warning("Please type something to submit.")
    st.stop()

# -----------------------------
# AFTER LOGIN
# -----------------------------
ist = pytz.timezone("Asia/Kolkata")
now = datetime.now(ist)
current_hour = now.hour
if 4 <= current_hour < 12:
    greeting = "Good Morning"
elif 12 <= current_hour < 16:
    greeting = "Good Afternoon"
elif 16 <= current_hour < 21:
    greeting = "Good Evening"
else:
    greeting = "Hello"

full_name_parts = st.session_state.logged_in_user.strip().replace(".", "").split()
first_name = next((p.title() for p in full_name_parts if p.upper() not in ["MR", "MISS"]), full_name_parts[0].title())

st.markdown(
    f"<div style='background-color:#e8f5e9;padding:14px;border-radius:10px;text-align:center;margin-bottom:15px;'>"
    f"<span style='color:#28a745;font-size:30px;font-weight:bold;'>{greeting}, {first_name}!</span>"
    f"</div>", unsafe_allow_html=True
)

st.markdown("""
<style>
div.stButton > button {
    background-color: #28a745 !important;
    color: white !important;
    font-size: 22px !important;
    font-weight: bold !important;
    padding: 0.7em 1.5em !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

if st.button("Logout"):
    for key in defaults.keys():
        st.session_state[key] = None
    st.rerun()

# -----------------------------
# OPTION SELECT PAGE
# -----------------------------
if st.session_state.query_option is None:
    st.markdown("<h2 style='color:#FF5733; font-weight:bold;'>Select Option</h2>", unsafe_allow_html=True)
    st.markdown("""
    <style>
    div[role="radiogroup"] > label {
        font-size: 26px !important;
        font-weight: bold !important;
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)

    choice = st.radio(
        "",
        [
            "Separate Pack",
            "Set",
            "Plasma Query",
            "ETO Query",
            "Autoclave Query",
            "5th Floor Handover",
            "3rd Floor Handover",
            "Set Identification"
        ]
    )
    if st.button("Continue", type="primary"):
        st.session_state.query_option = choice
        st.rerun()
    st.stop()

option = st.session_state.query_option
if st.button("⬅ Back"):
    st.session_state.query_option = None
    st.rerun()

# -----------------------------
# ISSUE LOG
# -----------------------------
LOG_FILE = "issue_log.csv"
if os.path.exists(LOG_FILE):
    log_df = pd.read_csv(LOG_FILE, engine="python", on_bad_lines="skip")
    if "SisterName" not in log_df.columns:
        log_df["SisterName"] = ""
else:
    log_df = pd.DataFrame(columns=["DateTime", "Technician", "SisterName", "Floor", "ItemName", "Department"])

# -----------------------------
# FEATURE SECTIONS
# -----------------------------
if option == "Separate Pack":
    from sap import separate_pack_section
    log_df = separate_pack_section(log_df, LOG_FILE, st.session_state.logged_in_user)

elif option == "Set":
    log_df = search_and_issue_sets(log_df, LOG_FILE, st.session_state.logged_in_user)

elif option == "Plasma Query":
    st.markdown("## Plasma / Instrument Recognition")
    from embeddings import InstrumentRecognizer

    recognizer = InstrumentRecognizer("plasma.csv")  # CSV with item_name,image_url,embedding
    uploaded_file = st.file_uploader("Upload instrument image", type=["jpg","png","jpeg"])

    if uploaded_file:
        st.image(uploaded_file, width=250)
        try:
            results = recognizer.recognize(uploaded_file, top_k=1)
            if not results.empty:
                top_file = results.iloc[0]["item_name"]
                sim = results.iloc[0]["similarity"]
                st.success(f"Best match: {top_file} (Similarity: {sim:.2f})")
            else:
                st.warning("No match found.")
        except Exception as e:
            st.error(f"Recognition failed: {e}")

else:
    st.info("Upcoming Feature")

# -----------------------------
# ISSUE HISTORY
# -----------------------------
st.subheader("Issue History")
if not log_df.empty:
    st.dataframe(log_df)
else:
    st.write("No issues recorded")

if st.button("Clear Log History"):
    pd.DataFrame(columns=["DateTime", "Technician", "SisterName", "Floor", "ItemName", "Department"]).to_csv(LOG_FILE, index=False)
    st.success("Log Cleared Successfully")
    st.rerun()