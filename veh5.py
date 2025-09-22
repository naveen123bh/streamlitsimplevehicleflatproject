import os
import re
import sys
import openpyxl
import streamlit as st
import pandas as pd

# ===== Heading =====
st.markdown("<h1 style='text-align:center; color:#FF5733; font-size:70px;'>Rishabh Tower Security</h1>", unsafe_allow_html=True)

# ===== Python version check =====
st.write("Python version:", sys.version)
st.write("openpyxl version:", openpyxl.__version__)

# ===== App Title =====
st.markdown("<h1 style='text-align:center; color:#1F618D; font-size:60px;'>Vehicle ↔ Flat Number App</h1>", unsafe_allow_html=True)

# ===== File setup =====
default_file = "vehnew.xlsx"
if not os.path.exists(default_file):
    st.error(f"File not found: {default_file}")
    st.stop()

try:
    df = pd.read_excel(default_file)
    st.success(f"File '{default_file}' loaded successfully!")
except Exception as e:
    st.error(f"Error reading file '{default_file}': {e}")
    st.stop()

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
    return text.strip()

df["Vehicle"] = df["Vehicle"].apply(normalize_vehicle_input)
df["FlatNumber"] = df["FlatNumber"].apply(normalize_flat_input)

# ===== Custom CSS for input, button, results =====
st.markdown("""
<style>
/* Input box style */
.big-input input {
    font-size: 60px !important;
    color: #D35400;
    font-weight: bold;
    text-align: center;
    height: 80px;
    border: 4px solid #1F618D;
    border-radius: 15px;
    background-color: #FCF3CF;
}

/* Button style */
.big-button button {
    font-size: 60px !important;
    background-color: #28B463;
    color: white;
    font-weight: bold;
    padding: 25px 50px;
    border-radius: 15px;
    width: 400px;
    display: block;
    margin: 30px auto;
}

/* Result messages style */
.stSuccess, .stWarning, .stError {
    font-size: 60px !important;
    font-weight: bold;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ===== Input box =====
user_input = st.text_input("Vehicle या Flat Number डालें", "", key="user_input")
st.markdown('<div class="big-input"></div>', unsafe_allow_html=True)

# ===== Button =====
if st.button("Result देखें", key="result_button"):
    if user_input:
        input_norm_vehicle = normalize_vehicle_input(user_input)
        input_norm_flat = normalize_flat_input(user_input)

        vehicle_rows = df[df["Vehicle"] == input_norm_vehicle]
        if not vehicle_rows.empty:
            flats = ", ".join(vehicle_rows["FlatNumber"].tolist())
            st.success(f"Vehicle {input_norm_vehicle} का Flat number(s): {flats}")
        else:
            flat_rows = df[df["FlatNumber"] == input_norm_flat]
            if not flat_rows.empty:
                vehicles = ", ".join(flat_rows["Vehicle"].tolist())
                st.success(f"Flat {input_norm_flat} का Vehicle number(s): {vehicles}")
            else:
                st.warning(
                    "वाहन सूची अपडेट की जा रही है। कार्य प्रगति में है।\n"
                    "कृपया 2 दिन प्रतीक्षा करें: लेखक इस पर काम कर रहे हैं।"
                )
    else:
        st.error("कृपया Vehicle या Flat Number दर्ज करें।")
