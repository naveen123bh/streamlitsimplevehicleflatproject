# this code is programmed by naveen123
import os
import random
import streamlit as st
import pandas as pd
import difflib
from technician import TECHNICIAN_NAMES
from sapset import search_and_issue_sets
from datetime import datetime
import pytz
from quotes import get_random_quote

# ============================
# SESSION STATE INIT
# ============================
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

# ==============================
# HELPER FUNCTION
# ==============================
def clean_name(name):
    name = name.upper().replace(".", "").replace("!", "").strip()
    for title in ["MR", "MISS"]:
        if name.startswith(title + " "):
            name = name[len(title)+1:]
    name = " ".join(name.split())
    return name

# ==============================
# LOGIN PAGE ONLY
# ==============================
if st.session_state.logged_in_user is None:

    hospital_image_url = "https://i.ibb.co/7NYqvcHz/hospital.jpg"
    st.image(hospital_image_url, width=400)

    st.markdown("<h2 style='color:purple;'>KDAH</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:green;'>Coded for CSSD Department</h4>", unsafe_allow_html=True)
    st.markdown("<p style='color:orange;'>Note: App is under consideration and development </p>", unsafe_allow_html=True)

    st.markdown("<h4 style='color:#444;'>Quote of the Moment</h4>", unsafe_allow_html=True)
    quote = get_random_quote()
    st.info(quote)

    # ==============================
    # PREPARE RANDOM SONG
    # ==============================
    current_dir = os.path.dirname(os.path.abspath(__file__))

    mp3_files = [
        os.path.join(current_dir, f)
        for f in os.listdir(current_dir)
        if f.lower().endswith(".mp3")
    ]

    if mp3_files:
        st.session_state["login_song"] = random.choice(mp3_files)
    else:
        st.warning("No mp3 files found in this folder")

    # ==============================

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

            # PLAY SONG ON LOGIN CLICK
            if "login_song" in st.session_state:
                st.audio(st.session_state["login_song"], autoplay=True)

            st.session_state.logged_in_user = st.session_state.login_selected_name
            st.rerun()
        else:
            st.warning("Enter correct name")

    st.stop()

# ==============================
# AFTER LOGIN
# ==============================

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

st.success(f"{greeting}, {first_name}!")

if st.button("Logout"):
    for key in defaults.keys():
        st.session_state[key] = None
    st.rerun()

# =============================
# OPTION SELECT PAGE
# ==============================
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
            "ETO Query",
            "Plasma Query",
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

# ==============================
# ISSUE LOG
# ==============================
LOG_FILE = "issue_log.csv"

if os.path.exists(LOG_FILE):
    log_df = pd.read_csv(LOG_FILE, engine="python", on_bad_lines="skip")
    if "SisterName" not in log_df.columns:
        log_df["SisterName"] = ""
else:
    log_df = pd.DataFrame(
        columns=["DateTime", "Technician", "SisterName", "Floor", "ItemName", "Department"]
    )

# ==============================
# FEATURE SECTIONS
# ==============================
if option == "Separate Pack":
    from sap import separate_pack_section
    log_df = separate_pack_section(
        log_df,
        LOG_FILE,
        st.session_state.logged_in_user
    )

elif option == "Set":
    log_df = search_and_issue_sets(
        log_df,
        LOG_FILE,
        st.session_state.logged_in_user
    )

else:
    st.info("Upcoming Feature")

# ==============================
# ISSUE HISTORY
# ==============================
st.subheader("Issue History")

if not log_df.empty:
    st.dataframe(log_df)
else:
    st.write("No issues recorded")

if st.button("Clear Log History"):
    empty_df = pd.DataFrame(
        columns=["DateTime", "Technician", "SisterName", "Floor", "ItemName", "Department"]
    )
    empty_df.to_csv(LOG_FILE, index=False)
    st.success("Log Cleared Successfully")
    st.rerun()