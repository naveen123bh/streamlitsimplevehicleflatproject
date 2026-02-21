import os
import re
import sys
import openpyxl
import streamlit as st
import pandas as pd
import difflib

# ===== Python version check =====
st.write("Python version:", sys.version)
st.write("openpyxl version:", openpyxl.__version__)

# ===== App Heading =====
st.markdown(
    "<h1 style='color:blue; font-size:60px;'>kokilaben hospital CSSD Set Floor Finder</h1>",
    unsafe_allow_html=True,
)

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
        engine="python",
        on_bad_lines="skip",
        encoding="utf-8"
    )
    st.success(f"File '{raw_file}' loaded successfully!")
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

df.to_csv(clean_file, index=False)

# ===== Build dictionaries =====
set_floor_pairs = dict(zip(df["SetName"], df["Floor"]))

floor_to_sets = {}
for set_name, floor in set_floor_pairs.items():
    floor_to_sets.setdefault(floor, []).append(set_name)

# ===== Streamlit Input =====
st.markdown(
    "<h3 style='color:green; font-size:40px;'>Set Name या Floor डालें</h3>",
    unsafe_allow_html=True,
)

user_input = st.text_input(
    "",
    "",
    key="set_floor_input",
    placeholder="Enter Set Name or Floor....",
    max_chars=100,
)

# ===== Button Styling =====
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

# ===== Lookup Logic =====
if st.button("Find Floor"):
    input_norm_set = normalize_set_input(user_input)
    input_norm_floor = normalize_floor_input(user_input)

    # ---- Exact Set Match ----
    if input_norm_set in set_floor_pairs:
        st.markdown(
            f"<h2 style='color:red; font-size:50px;'>Set '{input_norm_set}' should go to: {set_floor_pairs[input_norm_set]}</h2>",
            unsafe_allow_html=True,
        )

    # ---- Floor Lookup ----
    elif input_norm_floor in floor_to_sets:
        matched_sets = floor_to_sets[input_norm_floor]
        st.markdown(
            f"<h2 style='color:red; font-size:40px;'>Sets for {input_norm_floor}:</h2>",
            unsafe_allow_html=True,
        )
        for s in matched_sets:
            st.write(f"👉 {s}")

    # ---- Suggest Similar Sets ----
    else:
        suggestions = difflib.get_close_matches(
            input_norm_set,
            set_floor_pairs.keys(),
            n=5,
            cutoff=0.6,
        )

        if suggestions:
            st.markdown(
                "<h2 style='color:orange; font-size:40px;'>Set not found. Did you mean:</h2>",
                unsafe_allow_html=True,
            )
            for suggestion in suggestions:
                st.write(f"👉 {suggestion}")
        else:
            st.markdown(
                "<h2 style='color:red; font-size:50px;'>Set not found in database.<br>"
                "Please check spelling.</h2>",
                unsafe_allow_html=True,
            )