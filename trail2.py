import os
import streamlit as st
import pandas as pd
import difflib
from technician import TECHNICIAN_NAMES
from sapset import search_and_issue_sets
from datetime import datetime
import pytz
import random

# ==============================
# HOSPITAL IMAGE + HEADER
# ==============================
hospital_image_url = "https://i.ibb.co/7NYqvcHz/hospital.jpg"
st.image(hospital_image_url, width=400)
st.markdown("<h2 style='color:purple;'>KDAH</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:orange;'>Note: App is under consideration and development </p>", unsafe_allow_html=True)

# ==============================
# SESSION STATE INIT
# ==============================
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
# RANDOM DEEP QUOTES (2 lines each)
# ==============================
QUOTES = [
    "The mind is a mirror, see the reflection, not the shadow.\nPeace is the awareness of what is.",
    "Everything happens by itself; the doer is an illusion.\nWitness the flow and be free.",
    "Silence carries the answer; the world is but a play.\nBe the observer, not the actor.",
    "When you stop chasing, you arrive.\nWhat is, is enough for this moment.",
    "Nothing belongs to you, yet everything unfolds within you.\nLet love arise without effort."
]

def get_random_quote():
    return random.choice(QUOTES)

# ==============================
# LOGIN
# ==============================
if st.session_state.logged_in_user is None:

    name_input = st.text_input("Technician Name")

    if name_input:
        cleaned = " ".join(name_input.upper().split())
        normalized = {" ".join(n.upper().split()): n for n in TECHNICIAN_NAMES}

        if cleaned in normalized:
            st.session_state.login_selected_name = normalized[cleaned]
        else:
            suggestions = difflib.get_close_matches(cleaned, normalized.keys(), n=5, cutoff=0.5)
            if suggestions:
                options = [normalized[s] for s in suggestions]
                st.session_state.login_selected_name = st.selectbox("Did you mean:", options)

    if st.button("Login"):
        if st.session_state.login_selected_name:
            st.session_state.logged_in_user = st.session_state.login_selected_name
            st.rerun()
        else:
            st.warning("Enter correct name")

    st.stop()

# ==============================
# GREETING + QUOTE + LOGOUT
# ==============================
ist = pytz.timezone("Asia/Kolkata")
current_hour = datetime.now(ist).hour

# Determine greeting based on your specification
if 4 <= current_hour < 12:
    greeting = "Good Morning"
elif 12 <= current_hour < 16:
    greeting = "Good Afternoon"
elif 16 <= current_hour < 21:
    greeting = "Good Evening"
else:
    greeting = "Hello"

# Extract first name
first_name = st.session_state.logged_in_user.strip().split()[0].title()

# Display greeting + first name + random quote
st.success(f"{greeting}, {first_name}!\n\n{get_random_quote()}")

if st.button("Logout"):
    for key in defaults.keys():
        st.session_state[key] = None
    st.rerun()

# ==============================
# OPTION SELECT
# ==============================
if st.session_state.query_option is None:

    choice = st.radio("Select Option", ["Separate Pack", "Set"])

    if st.button("Continue"):
        st.session_state.query_option = choice
        st.rerun()

    st.stop()

option = st.session_state.query_option

# ==============================
# ISSUE LOG
# ==============================
LOG_FILE = "issue_log.csv"

if os.path.exists(LOG_FILE):
    log_df = pd.read_csv(LOG_FILE, engine="python", on_bad_lines="skip")
else:
    log_df = pd.DataFrame(
        columns=["DateTime", "Technician", "Floor", "ItemName", "Department"]
    )

# ==============================
# SEPARATE PACK
# ==============================
if option == "Separate Pack":
    from sap import separate_pack_section
    log_df = separate_pack_section(
        log_df,
        LOG_FILE,
        st.session_state.logged_in_user
    )

# ==============================
# SET SECTION
# ==============================
else:
    log_df = search_and_issue_sets(
        log_df,
        LOG_FILE,
        st.session_state.logged_in_user
    )

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
        columns=["DateTime", "Technician", "Floor", "ItemName", "Department"]
    )

    empty_df.to_csv(LOG_FILE, index=False)

    st.success("Log Cleared Successfully")
    st.rerun()