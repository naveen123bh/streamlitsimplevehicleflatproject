import os
import streamlit as st
import pandas as pd
import difflib

# ==================================
# KDHA HEADER & NOTE
# ==================================
st.markdown("<h2 style='color:purple; font-weight:bold;'>KDHA</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:orange; font-style:italic;'>Note: This app is under development and consideration</p>", unsafe_allow_html=True)

# ==================================
# CSSD TECHNICIAN MASTER LIST
# ==================================
TECHNICIAN_NAMES = [
    "MR. MANISH SHENVI","MISS SAUNDARYA JADHAV","MR. SANTOSH CHANDGUDE",
    "MR. AKSHAY GURAV","MR. NIKHIL KADAM","MISS SNEHA VISHVAKARMA",
    "MISS RUPAL MAHADAYE","MR. RAHUL SAWANT","MR. PADMAKAR JAGTAP",
    "MR. RAKESH MORE","MR. VINOD NIRAVDEKAR","MR. HRISHIKESH PARAB",
    "MR. SMITHIL POWAR","MR. AMAN SHUKLA","MR. MAYURAJ KADAM",
    "MR. SURESH LAMBARE","MR. PAWAN MASUDKAR","MR. JAVASH KAMTEKAR",
    "MISS MRUDULA CHAVAN","MR. FARHAN AHMED","MR. SANKET SUTAR",
    "MISS BHAGYASHRI MALANDKAR","MR. DEVENDRA DEVLEKAR","MR. NAVEEN KUMAR",
]

# ==================================
# SESSION STATE
# ==================================
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "current_floor" not in st.session_state:
    st.session_state.current_floor = None
if "current_set" not in st.session_state:
    st.session_state.current_set = None

# ==================================
# LOGIN
# ==================================
if st.session_state.logged_in_user is None:

    st.markdown("<h2 style='color:blue;'>CSSD Technician - Please enter your name here</h2>", unsafe_allow_html=True)
    name_input = st.text_input("Enter Your Name")

    if name_input:
        cleaned_input = " ".join(name_input.upper().split())
        normalized_names = { " ".join(name.upper().split()): name for name in TECHNICIAN_NAMES }

        if cleaned_input in normalized_names:
            st.session_state.logged_in_user = normalized_names[cleaned_input]
            st.rerun()
        else:
            suggestions = difflib.get_close_matches(cleaned_input, normalized_names.keys(), n=5, cutoff=0.5)
            if suggestions:
                st.info("Select your correct name:")
                for s in suggestions:
                    original_name = normalized_names[s]
                    if st.button(original_name):
                        st.session_state.logged_in_user = original_name
                        st.rerun()
            else:
                st.warning("please enter full name .")
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
if not os.path.exists("sets.csv"):
    st.error("sets.csv file not found.")
    st.stop()

df = pd.read_csv("sets.csv", engine="python", on_bad_lines="skip")
df = df.iloc[:, :2]
df.columns = ["SetName", "Floor"]

df["SetName"] = df["SetName"].astype(str).str.upper().str.strip()
df["Floor"] = df["Floor"].astype(str).str.upper().str.strip()

set_floor_pairs = dict(zip(df["SetName"], df["Floor"]))

# ==================================
# ISSUE LOG
# ==================================
LOG_FILE = "issue_log.csv"
if os.path.exists(LOG_FILE):
    log_df = pd.read_csv(LOG_FILE)
else:
    log_df = pd.DataFrame(columns=["Technician", "Floor", "SetName"])

for col in ["Technician","Floor","SetName"]:
    if col not in log_df.columns:
        log_df[col] = ""

log_df = log_df[["Technician","Floor","SetName"]]

# ==================================
# SEARCH SECTION
# ==================================
st.markdown("### Enter Set Name")
user_input = st.text_input("Search Here", key="search_input")

# Press Enter or button
search_pressed = st.button("Find Floor")

# ===== Handle search =====
if search_pressed or user_input:
    search = user_input.upper().strip()
    matched_set = None

    # Exact match
    if search in set_floor_pairs:
        st.session_state.current_floor = set_floor_pairs[search]
        st.session_state.current_set = search
        matched_set = search
    else:
        suggestions = difflib.get_close_matches(search, set_floor_pairs.keys(), n=5, cutoff=0.6)
        if suggestions:
            st.warning("Did you mean:")
            for s in suggestions:
                if st.button(s):
                    st.session_state.current_floor = set_floor_pairs[s]
                    st.session_state.current_set = s
                    matched_set = s
        else:
            # If no match, still show input as set name
            st.session_state.current_set = search
            st.session_state.current_floor = "Unknown Floor"
            matched_set = search

# ==================================
# SHOW FLOOR + ISSUE BUTTON
# ==================================
if st.session_state.current_floor:
    floor_name = st.session_state.current_floor
    set_name = st.session_state.current_set

    st.success(f"Floor ➜ {floor_name}")
    st.info(f"Yah set {floor_name} bheja jata hai.")

    if st.button("Issue"):
        new_entry = {
            "Technician": st.session_state.logged_in_user,
            "Floor": floor_name,
            "SetName": set_name
        }
        log_df = pd.concat([log_df, pd.DataFrame([new_entry])], ignore_index=True)
        log_df.to_csv(LOG_FILE, index=False)
        st.success(f"{set_name} issued successfully")

# ==================================
# ISSUE HISTORY + CLEAR LOG
# ==================================
st.markdown("### Issue History")
col1, col2 = st.columns([3,1])

with col2:
    if st.button("Clear Log"):
        log_df = pd.DataFrame(columns=["Technician","Floor","SetName"])
        log_df.to_csv(LOG_FILE,index=False)
        st.success("Issue history cleared")
        st.rerun()

if not log_df.empty:
    for index,row in log_df.iterrows():
        st.write(f"{row['Floor']} issued by {row['Technician']} (Set: {row['SetName']})")
else:
    st.write("No issues recorded yet.")