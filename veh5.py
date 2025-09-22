import os
import re
import sys
import openpyxl
import streamlit as st
import pandas as pd

# ===== Python version check =====
st.write("Python version:", sys.version)
st.write("openpyxl version:", openpyxl.__version__)

# ===== Heading =====
st.markdown("<h1 style='text-align:center; color:#1F618D; font-size:70px;'>Rishabh tower security</h1>", unsafe_allow_html=True)

# ===== File setup =====
default_file = "vehnew.xlsx"  # relative path, file is in the same folder as your script

# Check if file exists
if not os.path.exists(default_file):
    st.error(f"File not found: {default_file}")
    st.stop()

try:
    df = pd.read_excel(default_file)
    st.success(f"File '{default_file}' loaded successfully!")
except Exception as e:
    st.error(f"Error reading file '{default_file}': {e}")
    st.stop()

# ===== Handle column mismatch =====
if df.shape[1] < 2:
    st.error("Excel file must have at least 2 columns: Vehicle and FlatNumber")
    st.stop()

# Keep only first two columns and rename
df = df.iloc[:, :2]
df.columns = ["Vehicle", "FlatNumber"]

# ===== Helper functions =====
def normalize_vehicle_input(vehicle_number):
    """Normalize vehicle number: case-insensitive, remove spaces/newlines, replace O with 0."""
    if pd.isna(vehicle_number):
        return ""
    text = str(vehicle_number).upper()
    text = re.sub(r"\s+", "", text)        # remove ALL whitespace (spaces, tabs, newlines)
    text = text.replace("O", "0")          # replace letter O with zero
    return text.strip()

def normalize_flat_input(flat_number):
    """Normalize flat number: case-insensitive, remove spaces/newlines."""
    if pd.isna(flat_number):
        return ""
    text = str(flat_number).upper()
    text = re.sub(r"\s+", "", text)        # remove ALL whitespace
    return text.strip()

# ===== Normalize dataframe =====
df["Vehicle"] = df["Vehicle"].apply(normalize_vehicle_input)
df["FlatNumber"] = df["FlatNumber"].apply(normalize_flat_input)

# ===== Input =====
st.markdown("<h2 style='text-align:center; color:#D35400; font-size:40px;'>Vehicle या Flat Number डालें</h2>", unsafe_allow_html=True)
user_input = st.text_input("", "", key="user_input")

# ===== Lookup button =====
if st.button("Result देखें", key="lookup_button", help="Click to get Vehicle/Flat info"):
    if user_input:
        input_norm_vehicle = normalize_vehicle_input(user_input)
        input_norm_flat = normalize_flat_input(user_input)

        # Check if input matches any Vehicle
        vehicle_rows = df[df["Vehicle"] == input_norm_vehicle]
        if not vehicle_rows.empty:
            flats = ", ".join(vehicle_rows["FlatNumber"].tolist())
            st.markdown(f"<h1 style='text-align:center; color:#196F3D; font-size:60px;'>Flat number(s) for vehicle {input_norm_vehicle}: {flats}</h1>", unsafe_allow_html=True)
        else:
            # Check if input matches any FlatNumber
            flat_rows = df[df["FlatNumber"] == input_norm_flat]
            if not flat_rows.empty:
                vehicles = ", ".join(flat_rows["Vehicle"].tolist())
                st.markdown(f"<h1 style='text-align:center; color:#196F3D; font-size:60px;'>Vehicle number(s) for flat {input_norm_flat}: {vehicles}</h1>", unsafe_allow_html=True)
            else:
                st.markdown("<h1 style='text-align:center; color:#C0392B; font-size:60px;'>वाहन सूची अपडेट की जा रही है। कार्य प्रगति में है..<br>कृपया 2 दिन प्रतीक्षा करें: लेखक इस पर काम कर रहे हैं।</h1>", unsafe_allow_html=True)
