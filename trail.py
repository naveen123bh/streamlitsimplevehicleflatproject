import os
import re
import streamlit as st
import pandas as pd
import difflib

# ==================================
# CSSD TECHNICIAN MASTER LIST (24)
# ==================================
TECHNICIAN_NAMES = [
    "MR. MANISH SHENVI",
    "MISS SAUNDARYA JADHAV",
    "MR. SANTOSH CHANDGUDE",
    "MR. AKSHAY GURAV",
    "MR. NIKHIL KADAM",
    "MISS SNEHA VISHVAKARMA",
    "MISS RUPAL MAHADAYE",
    "MR. RAHUL SAWANT",
    "MR. PADMAKAR JAGTAP",
    "MR. RAKESH MORE",
    "MR. VINOD NIRAVDEKAR",
    "MR. HRISHIKESH PARAB",
    "MR. SMITHIL POWAR",
    "MR. AMAN SHUKLA",
    "MR. MAYURAJ KADAM",
    "MR. SURESH LAMBARE",
    "MR. PAWAN MASUDKAR",
    "MR. JAVASH KAMTEKAR",
    "MISS MRUDULA CHAVAN",
    "MR. FARHAN AHMED",
    "MR. SANKET SUTAR",
    "MISS BHAGYASHRI MALANDKAR",
    "MR. DEVENDRA DEVLEKAR",
    "MR. NAVEEN KUMAR",
]

# ==================================
# SESSION STATE
# ==================================
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if "current_floor" not in st.session_state:
    st.session_state.current_floor = None

# ==================================
# LOGIN SECTION
# ==================================
if st.session_state.logged_in_user is None:

    st.markdown("<h2 style='color:blue;'>CSSD Technician - Please enter your name here</h2>", unsafe_allow_html=True)

    name_input = st.text_input("Enter Your Name")
    name_upper = name_input.strip().upper()

    if name_upper:

        if name_upper in TECHNICIAN_NAMES:
            st.session_state.logged_in_user = name_upper
            st.rerun()
        else:
            suggestions = difflib.get_close_matches(name_upper, TECHNICIAN_NAMES, n=5, cutoff=0.5)

            if suggestions:
                st.info("Select your correct name:")
                for s in suggestions:
                    if st.button(s):
                        st.session_state.logged_in_user = s
                        st.rerun()
            else:
                st.warning("Name not recognized.")

    st.stop()

# ==================================
# AFTER LOGIN
# ==================================
st.success(f"Logged in as: {st.session_state.logged_in_user}")

if st.button("Logout"):
    st.session_state.logged_in_user = None
    st.rerun()

st.markdown("<h1 style='color:blue;'>CSSD Set Floor Finder</h1>", unsafe_allow_html=True)

# ==================================
# LOAD CSV
# ==================================
df = pd.read_csv("sets.csv")
df.columns = ["SetName", "Floor"]

df["SetName"] = df["SetName"].str.upper().str.strip()
df["Floor"] = df["Floor"].str.upper().str.strip()

set_floor_pairs = dict(zip(df["SetName"], df["Floor"]))

# ==================================
# ISSUE LOG
# ==================================
LOG_FILE = "issue_log.csv"

if os.path.exists(LOG_FILE):
    log_df = pd.read_csv(LOG_FILE)
else:
    log_df = pd.DataFrame(columns=["Technician", "Floor"])

# ==================================
# SEARCH
# ==================================
st.markdown("### Enter Set Name")
user_input = st.text_input("Search Here")

if user_input:
    search = user_input.upper().strip()

    if search in set_floor_pairs:
        st.session_state.current_floor = set_floor_pairs[search]

    else:
        suggestions = difflib.get_close_matches(search, set_floor_pairs.keys(), n=5, cutoff=0.6)

        if suggestions:
            st.warning("Did you mean:")
            for s in suggestions:
                if st.button(s):
                    st.session_state.current_floor = set_floor_pairs[s]

# ==================================
# SHOW FLOOR + ISSUE BUTTON
# ==================================
if st.session_state.current_floor:
    floor_name = st.session_state.current_floor
    st.success(f"Floor ➜ {floor_name}")

    if st.button("Issue"):
        new_entry = {
            "Technician": st.session_state.logged_in_user,
            "Floor": floor_name
        }

        log_df = pd.concat([log_df, pd.DataFrame([new_entry])], ignore_index=True)
        log_df.to_csv(LOG_FILE, index=False)

        st.success(f"{floor_name} issued successfully")

# ==================================
# HISTORY
# ==================================
st.markdown("### Issue History")

if not log_df.empty:
    for index, row in log_df.iterrows():
        st.write(f"{row['Floor']} issued by {row['Technician']}")
else:
    st.write("No issues recorded yet.")