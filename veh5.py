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

# Keep only first two columns
df = df.iloc[:, :2]
df.columns = ["Vehicle", "FlatNumber"]

# ===== Helper functions =====
def normalize_vehicle_input(vehicle_number):
    if pd.isna(vehicle_number):
        return ""
    text = str(vehicle_number).upper()
    text = re.sub(r"\s+", "", text)
    text = text.replace("O", "0")  # O to zero
    return text.strip()

def normalize_flat_input(flat_number):
    if pd.isna(flat_number):
        return ""
    text = str(flat_number).upper()
    text = re.sub(r"\s+", "", text)
    if text.isnumeric():  # if user enters number like 1402
        text = "F" + text
    return text.strip()

# ===== Normalize dataframe =====
df["Vehicle"] = df["Vehicle"].apply(normalize_vehicle_input)
df["FlatNumber"] = df["FlatNumber"].apply(lambda x: "F"+str(x).strip().upper() if str(x).strip().isnumeric() else str(x).strip().upper())

# ===== Hardcoded vehicle → flat mapping =====
vehicle_flat_pairs = {
    "DL25M8883": "F706", "MH01AW0076": "F803", "MH01DV7905": "F803",
    "MH01BL4073": "F1001", "MH01CY4916": "F1101", "MH01DV4548": "F1101",
    "MH01AS7283": "F1103", "MH01BW8739": "F1201", "MH01AJ1280": "F1201",
    "MH01CW1103": "F1202", "MH01DN8388": "F1202", "MH01DS8388": "F1202",
    "MH01DF8883": "F1402", "MH47AG8208": "F1501", "MH01CS1389": "F1501",
    "MH01DF8922": "F1501", "MH02FT6906": "F301", "MH01VE9542": "F1404",
    "KL250825": "F702", "MH01BV4719": "F1503", "MH01DC4468": "F1103",
    "MH01EC4345": "F303", "MH01EG4466": "F1404", "MH01BR3809": "F1303",
    "MH01DH8262": "F1202", "MH01EC1731": "F103", "MH01EC6173": "F103",
    "MH01ED5928": "F104", "MH01BV9157": "F105", "MH01BS5970": "F406",
    "MH01BN6173": "F204", "MH01CZ8751": "F204", "MH46BC6962": "F205",
    "MH01CW8808": "F206", "MH01AY3291": "F306", "MH45P6581": "F401",
    "MHGJ10CE1771": "F403", "MH01Z4903": "F403", "MH01CW5160": "F403",
    "MH46DZ5084": "F403", "MH46AS5358": "F404", "MH01DM3960": "F405",
    "MH01CB5008": "F405", "MH01CZ0743": "F504", "MH01CX9174": "F505",
    "MH46BR6433": "F506", "MH46BX7368": "F506", "MH01RA3013": "F601",
    "MH14E7323": "F601", "MH14BS7612": "F605", "MH43BS6225": "F606",
    "JK02AJ9532": "F701", "MH01EG1167": "F701", "KL25P0885": "F702",
    "PB12N9278": "F502", "DL95BC4754": "F402", "DL95AY2413": "F501",
    "MH01ED1470": "F203", "MH01DD9066": "F705", "MH01DE8241": "F1104",
    "MH01DD0634": "F1105", "MHED4100": "F1203", "MH01AS5210": "F1203",
    "MH01CX5210": "F1204", "MH01DM8542": "F1304", "MH01BZ7329": "F1502",
    "MHO1CW8883":"F1402"  # example vehicle you mentioned
}

# Normalize dictionary keys
vehicle_flat_pairs = {normalize_vehicle_input(k): v for k, v in vehicle_flat_pairs.items()}

# ===== Streamlit Input =====
st.markdown("<h3 style='color:green; font-size:40px;'>Vehicle या Flat Number डालें</h3>", unsafe_allow_html=True)
user_input = st.text_input("", "", key="vehicle_flat_input", placeholder="Yahaa darj kare", max_chars=15)

# ===== Lookup Button =====
if st.button("रिज़ल्ट देखें", key="lookup_button"):
    input_norm_vehicle = normalize_vehicle_input(user_input)
    input_norm_flat = normalize_flat_input(user_input)

    if input_norm_vehicle in vehicle_flat_pairs:
        st.markdown(f"<h2 style='color:red; font-size:50px;'>Vehicle {input_norm_vehicle} का Flat Number है: {vehicle_flat_pairs[input_norm_vehicle]}</h2>", unsafe_allow_html=True)
    elif input_norm_flat in vehicle_flat_pairs.values():
        matched_vehicles = [v for v, f in vehicle_flat_pairs.items() if f == input_norm_flat]
        st.markdown(f"<h2 style='color:red; font-size:50px;'>Flat {input_norm_flat} के लिए Vehicle नंबर हैं: {', '.join(matched_vehicles)}</h2>", unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='color:red; font-size:50px;'>वाहन सूची अपडेट की जा रही है। कार्य प्रगति में है..<br>कृपया 2 दिन प्रतीक्षा करें: लेखक इस पर काम कर रहे हैं।</h2>", unsafe_allow_html=True)
