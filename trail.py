import os
import re
import sys
import openpyxl
import streamlit as st
import pandas as pd
import difflib

# ==============================
# CSSD TECHNICIAN MASTER LIST
# ==============================
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

# ==============================
# SESSION STATE FOR LOGIN
# ==============================
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# ==============================
# LOGIN SECTION
# ==============================
if st.session_state.logged_in_user is None:

    st.markdown(
        "<h2 style='color:blue;'>CSSD Technician - Please enter your name here</h2>",
        unsafe_allow_html=True,
    )

    name_input = st.text_input("Enter Your Name")

    if st.button("Login"):

        name_upper = name_input.strip().upper()

        # Exact match
        if name_upper in TECHNICIAN_NAMES:
            st.session_state.logged_in_user = name_upper
            st.rerun()

        # Suggestion logic
        else:
            suggestions = difflib.get_close_matches(
                name_upper,
                TECHNICIAN_NAMES,
                n=5,
                cutoff=0.6,
            )

            if suggestions:
                st.warning("Name not found. Did you mean:")
                for s in suggestions:
                    if st.button(s):
                        st.session_state.logged_in_user = s
                        st.rerun()
            else:
                st.error("Name not recognized. Please check spelling.")

    st.stop()

# ==============================
# AFTER LOGIN
# ==============================
st.success(f"Logged in as: {st.session_state.logged_in_user}")

# ==============================
# APP HEADER
# ==============================
st.markdown(
    "<h1 style='color:blue; font-size:50px;'>CSSD Set Floor Finder</h1>",
    unsafe_allow_html=True,
)

# ==============================
# HELPER FUNCTIONS
# ==============================
def normalize_set_input(set_name):
    if pd.isna(set_name):
        return ""
    text = str(set_name).upper()
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def normalize_floor_input(floor_name):
    if pd.isna(floor_name):
        return ""
    text = str(floor_name).upper()
    text = re.sub(r"\s+", "", text)
    return text.strip()

# ==============================
# LOAD CSV SAFELY
# ==============================
raw_file = "sets.csv"

if not os.path.exists(raw_file):
    st.error(f"File not found: {raw_file}")
    st.stop()

try:
    df = pd.read_csv(
        raw_file,
        engine="python",
        on_bad_lines="skip",
        encoding="utf-8"
    )
except Exception as e:
    st.error(f"Error reading file: {e}")
    st.stop()

if df.shape[1] < 2:
    st.error("CSV must contain at least 2 columns.")
    st.stop()

df = df.iloc[:, :2]
df.columns = ["SetName", "Floor"]

df["SetName"] = df["SetName"].apply(normalize_set_input)
df["Floor"] = df["Floor"].apply(normalize_floor_input)

set_floor_pairs = dict(zip(df["SetName"], df["Floor"]))

floor_to_sets = {}
for set_name, floor in set_floor_pairs.items():
    floor_to_sets.setdefault(floor, []).append(set_name)

# ==============================
# SEARCH SECTION
# ==============================
st.markdown("<h3>Enter Set Name or Floor</h3>")
user_input = st.text_input("Search Here")

if st.button("Find Floor"):

    input_norm_set = normalize_set_input(user_input)
    input_norm_floor = normalize_floor_input(user_input)

    # Exact Set Match
    if input_norm_set in set_floor_pairs:
        st.success(f"{input_norm_set} ➜ {set_floor_pairs[input_norm_set]}")

    # Floor Lookup
    elif input_norm_floor in floor_to_sets:
        st.info(f"Sets for {input_norm_floor}:")
        for s in floor_to_sets[input_norm_floor]:
            st.write(f"👉 {s}")

    # Suggest Similar Set Names
    else:
        suggestions = difflib.get_close_matches(
            input_norm_set,
            set_floor_pairs.keys(),
            n=5,
            cutoff=0.6,
        )

        if suggestions:
            st.warning("Set not found. Did you mean:")
            for s in suggestions:
                st.write(f"👉 {s}")
        else:
            st.error("Set not found in database.")