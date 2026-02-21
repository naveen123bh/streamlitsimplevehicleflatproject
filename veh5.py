import os
import re
import sys
import openpyxl
import streamlit as st
import pandas as pd

# ===== Python version check =====
st.write("Python version:", sys.version)
st.write("openpyxl version:", openpyxl.__version__)

# ===== App Heading =====
st.markdown("<h1 style='color:blue; font-size:60px;'>kokilaben hospital CSSD Set Floor Finder</h1>", unsafe_allow_html=True)

# ===== Helper functions =====
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

# ===== File setup =====
raw_file = "sets.csv"
clean_file = "sets_clean.csv"

if not os.path.exists(raw_file):
    st.error(f"File not found: {raw_file}")
    st.stop()

try:
    df = pd.read_csv(
        raw_file,
        engine="python",        # flexible parser
        on_bad_lines="skip",    # skip broken rows
        encoding="utf-8"
    )
    st.success(f"code scripted by naveen bhatt  file'{raw_file}' app is at initial phase!")
except Exception as e:
    st.error(f"Error reading file '{raw_file}': {e}")
    st.stop()

if df.shape[1] < 2:
    st.error("CSV file must have at least 2 columns: set_name and floor")
    st.stop()

# ===== Normalize dataframe =====
df = df.iloc[:, :2]
df.columns = ["SetName", "Floor"]

df["SetName"] = df["SetName"].apply(normalize_set_input)
df["Floor"] = df["Floor"].apply(normalize_floor_input)

# Save normalized clean file
df.to_csv(clean_file, index=False)

# ===== Build dictionaries =====
set_floor_pairs = dict(zip(df["SetName"], df["Floor"]))

floor_to_sets = {}
for set_name, floor in set_floor_pairs.items():
    if floor not in floor_to_sets:
        floor_to_sets[floor] = []
    floor_to_sets[floor].append(set_name)

# ===== Streamlit Input =====
st.markdown("<h3 style='color:green; font-size:40px;'>Set Name या Floor डालें</h3>", unsafe_allow_html=True)
user_input = st.text_input("", "", key="set_floor_input", placeholder="Enter Set Name or Floor....", max_chars=100)

# ===== Style the button =====
st.markdown("""
<style>
div.stButton > button {
    background-color: red;
    color: white;
    font-size: 36px;
    font-weight: bold;
    border-radius: 12px;
    padding: 15px 40px;
    border: 2px solid darkred;
}
div.stButton > button:hover {
    background-color: darkred;
}
</style>
""", unsafe_allow_html=True)

# ===== Lookup button =====
if st.button("Find Floor"):
    input_norm_set = normalize_set_input(user_input)
    input_norm_floor = normalize_floor_input(user_input)

    # ----- Exact Set lookup -----
    if input_norm_set in set_floor_pairs:
        st.markdown(
            f"<h2 style='color:red; font-size:50px;'>Set '{input_norm_set}' should go to: {set_floor_pairs[input_norm_set]}</h2>",
            unsafe_allow_html=True,
        )

    # ----- Floor lookup -----
    elif input_norm_floor in floor_to_sets:
        matched_sets = floor_to_sets[input_norm_floor]
        st.markdown(
            f"<h2 style='color:red; font-size:40px;'>Sets for {input_norm_floor}:</h2>",
            unsafe_allow_html=True,
        )
        for s in matched_sets:
            st.write(s)

    else:
        st.markdown(
            "<h2 style='color:red; font-size:50px;'>Set not found in database.<br>"
            "Please check spelling or confirm with supervisor.</h2>",
            unsafe_allow_html=True,
        )