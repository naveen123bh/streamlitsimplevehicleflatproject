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
st.markdown("<h1 style='color:blue; font-size:60px;'>Rishabh Tower Security</h1>", unsafe_allow_html=True)

# ===== File setup =====
default_file = "vehnew.xlsx"  # relative path
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

df = df.iloc[:, :2]
df.columns = ["Vehicle", "FlatNumber"]

# ===== Helper functions =====
def normalize_vehicle_input(vehicle_number):
    if pd.isna(vehicle_number):
        return ""
    text = str(vehicle_number).upper()
    text = re.sub(r"\s+", "", text)
    text = text.replace("O", "0")
    return text.strip()

def normalize_flat_input(flat_number):
    if pd.isna(flat_number):
        return ""
    text = str(flat_number).upper()
    text = re.sub(r"\s+", "", text)
    if text.isnumeric():  # automatically prefix F for numeric input
        text = f"F{text}"
    return text.strip()

# ===== Normalize dataframe =====
df["Vehicle"] = df["Vehicle"].apply(normalize_vehicle_input)
df["FlatNumber"] = df["FlatNumber"].apply(normalize_flat_input)

# ===== Hardcoded vehicle → flat mapping =====
vehicle_flat_pairs = {
    "DL25M8883": "F706", "MH01AW0076": "F803", "MH01DV7905": "F803",
    "MH01BL4073": "F1001", "MH01CY4916": "F1101", "MH01DV4548": "F1101",
    "MH01AS7283": "F1103", "MH01BW8739": "F1201", "MH01AJ1280": "F1201",
    "MH01CW1103": "F1202", "MH01DN8388": "F1202", "MH01DS8388": "F1202",
    "MH01DF8883": "F1402",
    "MHO1CW8883":"F1402",
    # ... (all other mappings unchanged)
}

# Ensure keys/values are uppercase and stripped
vehicle_flat_pairs = {k.strip().upper(): v.strip().upper() for k, v in vehicle_flat_pairs.items()}

# ===== Streamlit Input =====
st.markdown("<h3 style='color:green; font-size:40px;'>Vehicle या Flat Number डालें</h3>", unsafe_allow_html=True)
user_input = st.text_input("", "", key="vehicle_flat_input",
                           placeholder="Yahaa darj kare", max_chars=15)

# ===== Lookup Button =====
if st.button("रिज़ल्ट देखें", key="lookup_button"):
    input_norm_vehicle = normalize_vehicle_input(user_input)
    input_norm_flat = normalize_flat_input(user_input)

    # Lookup vehicle → flat
    if input_norm_vehicle in vehicle_flat_pairs:
        flat = vehicle_flat_pairs[input_norm_vehicle]
        st.markdown(f"<h2 style='color:red; font-size:50px;'>Vehicle {input_norm_vehicle} का Flat Number है: {flat}</h2>", unsafe_allow_html=True)

    # Lookup flat → vehicles (all matching vehicles)
    elif input_norm_flat in vehicle_flat_pairs.values():
        matched_vehicles = [v for v, f in vehicle_flat_pairs.items() if f == input_norm_flat]
        matched_vehicles_str = ", ".join(matched_vehicles)
        st.markdown(f"<h2 style='color:red; font-size:50px;'>Flat {input_norm_flat} के लिए Vehicle नंबर हैं: {matched_vehicles_str}</h2>", unsafe_allow_html=True)

    else:
        st.markdown("<h2 style='color:red; font-size:50px;'>वाहन सूची अपडेट की जा रही है। कार्य प्रगति में है..<br>कृपया 2 दिन प्रतीक्षा करें: लेखक इस पर काम कर रहे हैं।</h2>", unsafe_allow_html=True)
