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

# ==================================
# LOGIN SECTION
# ==================================
if st.session_state.logged_in_user is None:

    st.markdown(
        "<h2 style='color:blue;'>CSSD Technician - Please enter your name here</h2>",
        unsafe_allow_html=True,
    )

    name_input = st.text_input("Enter Your Name")
    name_upper = name_input.strip().upper()

    if name_upper:

        if name_upper in TECHNICIAN_NAMES:
            st.session_state.logged_in_user = name_upper
            st.success(f"Welcome {name_upper}")
            st.rerun()
        else:
            suggestions = difflib.get_close_matches(
                name_upper,
                TECHNICIAN_NAMES,
                n=5,
                cutoff=0.5,
            )

            if suggestions:
                st.info("Select your correct name:")
                for s in suggestions:
                    if st.button(s):
                        st.session_state.logged_in_user = s
                        st.success(f"Welcome {s}")
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

st.markdown(
    "<h1 style='color:blue; font-size:45px;'>CSSD Set Floor Finder</h1>",
    unsafe_allow_html=True,
)

# ==================================
# HELPER FUNCTIONS
# ==================================
def normalize_set_input(text):
    if pd.isna(text):
        return ""
    text = str(text).upper()
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def normalize_floor_input(text):
    if pd.isna(text):
        return ""
    text = str(text).upper()
    text = re.sub(r"\s+", "", text)
    return text.strip()

# ==================================
# LOAD CSV
# ==================================
raw_file = "sets.csv"

if not os.path.exists(raw_file):
    st.error("sets.csv file not found.")
    st.stop()

df = pd.read_csv(raw_file, engine="python", on_bad_lines="skip")

if df.shape[1] < 2:
    st.error("CSV must contain SetName and Floor columns.")
    st.stop()

df = df.iloc[:, :2]
df.columns = ["SetName", "Floor"]

df["SetName"] = df["SetName"].apply(normalize_set_input)
df["Floor"] = df["Floor"].apply(normalize_floor_input)

set_floor_pairs = dict(zip(df["SetName"], df["Floor"]))

floor_to_sets = {}
for set_name, floor in set_floor_pairs.items():
    floor_to_sets.setdefault(floor, []).append(set_name)

# ==================================
# ISSUE LOG SETUP
# ==================================
LOG_FILE = "issue_log.csv"

if os.path.exists(LOG_FILE):
    log_df = pd.read_csv(LOG_FILE)
else:
    log_df = pd.DataFrame(columns=["Technician", "Floor"])

# ==================================
# SEARCH SECTION
# ==================================
st.markdown("<h3>Enter Set Name or Floor</h3>")
user_input = st.text_input("Search Here")

input_norm_set = normalize_set_input(user_input)
input_norm_floor = normalize_floor_input(user_input)

def show_issue_option(floor_name):
    st.success(f"Floor ➜ {floor_name}")

    if st.button("Issue"):
        new_entry = {
            "Technician": st.session_state.logged_in_user,
            "Floor": floor_name
        }

        updated_log = pd.concat([log_df, pd.DataFrame([new_entry])], ignore_index=True)
        updated_log.to_csv(LOG_FILE, index=False)

        st.success(f"{floor_name} issued successfully")

# Exact match
if input_norm_set in set_floor_pairs:
    floor_found = set_floor_pairs[input_norm_set]
    show_issue_option(floor_found)

elif input_norm_floor in floor_to_sets:
    st.info(f"Sets for {input_norm_floor}:")
    for s in floor_to_sets[input_norm_floor]:
        st.write(f"👉 {s}")

elif user_input:

    suggestions = difflib.get_close_matches(
        input_norm_set,
        set_floor_pairs.keys(),
        n=5,
        cutoff=0.6,
    )

    if suggestions:
        st.warning("Set not found. Did you mean:")
        for s in suggestions:
            if st.button(s):
                floor_found = set_floor_pairs[s]
                show_issue_option(floor_found)
    else:
        st.error("Set not found in database.")

# ==================================
# ISSUE HISTORY
# ==================================
st.markdown("### Issue History")

if os.path.exists(LOG_FILE):
    history_df = pd.read_csv(LOG_FILE)

    if not history_df.empty:
        for index, row in history_df.iterrows():
            st.write(f"{row['Floor']} issued by {row['Technician']}")
    else:
        st.write("No issues recorded yet.")
else:
    st.write("No issues recorded yet.")