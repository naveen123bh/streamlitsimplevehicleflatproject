import os
import streamlit as st
import pandas as pd
import difflib
from technician import TECHNICIAN_NAMES
from sapset import search_and_issue_sets
from datetime import datetime
import pytz
from quotes import get_random_quote

# ==============================
# HEADER
# ==============================
hospital_image_url = "https://i.ibb.co/7NYqvcHz/hospital.jpg"
st.image(hospital_image_url, width=400)
st.markdown("<h2 style='color:purple;'>KDAH</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:orange;'>Note: App is under consideration and development </p>", unsafe_allow_html=True)

# ==============================
# QUOTE
# ==============================
st.markdown("<h4 style='color:#444;'>Quote of the Moment</h4>", unsafe_allow_html=True)
st.info(get_random_quote())

# ==============================
# SESSION STATE
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
# LOGIN
# ==============================
def clean_name(name):
    return name.upper().replace(".", "").strip()

if st.session_state.logged_in_user is None:
    name_input = st.text_input("Technician Name")
    if name_input:
        normalized = {clean_name(n): n for n in TECHNICIAN_NAMES}
        cleaned = clean_name(name_input)
        if cleaned in normalized:
            st.session_state.logged_in_user = normalized[cleaned]
            st.rerun()
        else:
            st.warning("Enter correct name")
    st.stop()

st.success(f"Welcome {st.session_state.logged_in_user}")

if st.button("Logout"):
    for key in defaults.keys():
        st.session_state[key] = None
    st.rerun()

# ==============================
# OPTION
# ==============================
if st.session_state.query_option is None:
    choice = st.radio("Select Option", ["Separate Pack", "Set"])
    if st.button("Continue"):
        st.session_state.query_option = choice
        st.rerun()
    st.stop()

option = st.session_state.query_option

# ==============================
# LOG INIT
# ==============================
LOG_FILE = "issue_log.csv"

if os.path.exists(LOG_FILE):
    log_df = pd.read_csv(LOG_FILE)
else:
    log_df = pd.DataFrame(
        columns=["DateTime","Technician","SisterName","Floor","ItemName","Department"]
    )

# ==============================
# ISSUE DETAILS (Only Addition)
# ==============================
st.subheader("Issue Details")
sister_name = st.text_input("Enter Sister Name")

# ==============================
# SEARCH FLOW (UNCHANGED)
# ==============================
if option == "Separate Pack":
    from sap import separate_pack_section
    log_df = separate_pack_section(
        log_df,
        LOG_FILE,
        st.session_state.logged_in_user,
        sister_name
    )
else:
    log_df = search_and_issue_sets(
        log_df,
        LOG_FILE,
        st.session_state.logged_in_user,
        sister_name
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
    pd.DataFrame(columns=log_df.columns).to_csv(LOG_FILE,index=False)
    st.success("Log Cleared Successfully")
    st.rerun()