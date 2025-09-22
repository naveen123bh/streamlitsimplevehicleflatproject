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
st.markdown("""
<h1 style='text-align:center; color:#1F618D; font-size:70px;'>
Rishabh tower security
</h1>
""", unsafe_allow_html=True)

# ===== File setup =====
default_file = "vehnew.xlsx"  # relative path, file is in the same folder as your script

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

# ===== Custom CSS for dark background and spacing =====
st.markdown("""
<style>
/* Dark background behind input area */
.input-container {
    background-color: #2C3E50;
    padding: 20px;
    border-radius: 15px;
    width: 80%;
    margin: 0 auto; /* center horizontally */
}

/* Input box styling */
div[data-testid="stTextInput"] input {
    height: 70px;           
    font-size: 35px;        
    border: 4px solid #1ABC9C; 
    border-radius: 10px;    
    padding-left: 15px;
    margin-top: 5px;
    width: 100%;
}

/* Lookup button styling */
div.stButton > button {
    font-size: 35px;
    padding: 15px 50px;
    background-color: #E67E22;
    color: white;
    border-radius: 15px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ===== Input area =====
st.markdown("<div class='input-container'>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align:center; color:#F1C40F; font-size:40px; margin-bottom:10px;'>Vehicle या Flat Number डालें</h2>", unsafe_allow_html=True)

user_input = st.text_input("", "", key="user_input", placeholder="यहाँ दर्ज करें")

st.markdown("<div style='text-align:center; margin-top:20px;'>", unsafe_allow_html=True)
if st.button("Result देखें", key="lookup_button"):
    if user_input:
        input_norm_vehicle = normalize_vehicle_input(user_input)
        input_norm_flat = normalize_flat_input(user_input)

        vehicle_rows = df[df["Vehicle"] == input_norm_vehicle]
        if not vehicle_rows.empty:
            flats = ", ".join(vehicle_rows["FlatNumber"].tolist())
            st.markdown(f"<h1 style='text-align:center; color:#196F3D; font-size:60px;'>{flats}</h1>", unsafe_allow_html=True)
        else:
            flat_rows = df[df["FlatNumber"] == input_norm_flat]
            if not flat_rows.empty:
                vehicles = ", ".join(flat_rows["Vehicle"].tolist())
                st.markdown(f"<h1 style='text-align:center; color:#196F3D; font-size:60px;'>{vehicles}</h1>", unsafe_allow_html=True)
            else:
                st.markdown("<h1 style='text-align:center; color:#C0392B; font-size:60px;'>वाहन सूची अपडेट की जा रही है। कार्य प्रगति में है..<br>कृपया 2 दिन प्रतीक्षा करें: लेखक इस पर काम कर रहे हैं।</h1>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
