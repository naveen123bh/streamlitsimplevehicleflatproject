import os
import re
import sys
import openpyxl
import streamlit as st
import pandas as pd

# ===== Python version check =====
st.write("Python version:", sys.version)
st.write("openpyxl version:", openpyxl.__version__)

# ===== Custom CSS for styling =====
st.markdown("""
<style>
/* Heading */
h1 {
    text-align: center;
    font-size: 70px;
    color: #e74c3c;
    font-weight: bold;
    margin-bottom: 40px;
}

/* Input label */
.input-label {
    text-align: center;
    color: #f1c40f;
    font-size: 40px;
    margin-bottom: 5px;
}

/* Input box */
.big-input input {
    height: 70px;
    font-size: 30px;
    border: 3px solid #3498DB;
    border-radius: 10px;
}

/* Button */
.stButton>button {
    width: 300px;
    height: 70px;
    font-size: 35px;
    background-color: #2ecc71;
    color: white;
    border-radius: 15px;
    display: block;
    margin-left: auto;
    margin-right: auto;
}

/* Output messages */
.success, .stSuccess {
    font-size: 40px !important;
    color: #27ae60 !important;
    text-align: center;
}
.error, .stError {
    font-size: 40px !important;
    color: #c0392b !important;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ===== App heading =====
st.markdown("<h1>Rishabh Tower Security</h1>", unsafe_allow_html=True)

# ===== File setup =====
default_file = "vehnew.xlsx"  # file should be in same folder

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
    return text.strip()

# ===== Normalize dataframe =====
df["Vehicle"] = df["Vehicle"].apply(normalize_vehicle_input)
df["FlatNumber"] = df["FlatNumber"].apply(normalize_flat_input)

# ===== Input area =====
st.markdown("<div class='input-label'>Vehicle या Flat Number डालें</div>", unsafe_allow_html=True)
user_input = st.text_input("", "", key="user_input", placeholder="यहाँ दर्ज करें", label_visibility="collapsed")

# ===== Lookup button =====
if st.button("Result देखें"):
    if user_input:
        input_norm_vehicle = normalize_vehicle_input(user_input)
        input_norm_flat = normalize_flat_input(user_input)

        # Check Vehicle match
        vehicle_rows = df[df["Vehicle"] == input_norm_vehicle]
        if not vehicle_rows.empty:
            flats = ", ".join(vehicle_rows["FlatNumber"].tolist())
            st.success(f"Vehicle {input_norm_vehicle} के लिए Flat Number: {flats}")
        else:
            # Check Flat match
            flat_rows = df[df["FlatNumber"] == input_norm_flat]
            if not flat_rows.empty:
                vehicles = ", ".join(flat_rows["Vehicle"].tolist())
                st.success(f"Flat {input_norm_flat} के लिए Vehicle Number: {vehicles}")
            else:
                st.error("वाहन सूची अपडेट की जा रही है। कार्य प्रगति में है..\nकृपया 2 दिन प्रतीक्षा करें: लेखक इस पर काम कर रहे हैं।")
