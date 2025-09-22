import os
import sys
import re
import openpyxl
import streamlit as st
import pandas as pd

# ===== Python version check =====
st.write("Python version:", sys.version)
st.write("openpyxl version:", openpyxl.__version__)

# ===== App Heading =====
st.markdown("<h1 style='color:blue; font-size:60px;'>Rishabh Tower Security</h1>", unsafe_allow_html=True)

# ===== File setup =====
default_file = "vehicle_flat_pairs.csv"

if not os.path.exists(default_file):
    st.error(f"File not found: {default_file}")
    st.stop()

try:
    df = pd.read_csv(default_file)
    st.success(f"File '{default_file}' loaded successfully!")
except Exception as e:
    st.error(f"Error reading file '{default_file}': {e}")
    st.stop()

if df.shape[1] < 2:
    st.error("CSV file must have at least 2 columns: Vehicle, FlatNumber")
    st.stop()

df = df.iloc[:, :2]
df.columns = ["Vehicle", "FlatNumber"]

# ===== Normalization helpers =====
def normalize_vehicle_input(vehicle_number: str) -> str:
    if pd.isna(vehicle_number):
        return ""
    text = str(vehicle_number).upper()
    text = re.sub(r"\\s+", "", text)
    return text.strip()

def normalize_flat_input(flat_number: str) -> str:
    if pd.isna(flat_number):
        return ""
    text = str(flat_number).upper()
    text = re.sub(r"\\s+", "", text)
    if text.isnumeric():
        text = "F" + text
    return text.strip()

# ===== Normalize dataframe =====
df["Vehicle"] = df["Vehicle"].apply(normalize_vehicle_input)
df["FlatNumber"] = df["FlatNumber"].apply(normalize_flat_input)

# ===== Build mappings =====
vehicle_flat_pairs = dict(zip(df["Vehicle"], df["FlatNumber"]))

flat_to_vehicles = {}
for vehicle, flat in vehicle_flat_pairs.items():
    flat_to_vehicles.setdefault(flat, []).append(vehicle)

# ===== Streamlit Input =====
st.markdown("<h3 style='color:green; font-size:40px;'>Vehicle या Flat Number डालें</h3>", unsafe_allow_html=True)
user_input = st.text_input("", "", key="vehicle_flat_input", placeholder="Yahaa darj kare", max_chars=15)

if st.button("रिज़ल्ट देखें", key="lookup_button"):
    input_norm_vehicle = normalize_vehicle_input(user_input)
    input_norm_flat = normalize_flat_input(user_input)

    # ----- Vehicle lookup -----
    if input_norm_vehicle in vehicle_flat_pairs:
        st.markdown(
            f"<h2 style='color:red; font-size:50px;'>Vehicle {input_norm_vehicle} का Flat Number है: {vehicle_flat_pairs[input_norm_vehicle]}</h2>",
            unsafe_allow_html=True,
        )

    # ----- Flat lookup: show all vehicles -----
    elif input_norm_flat in flat_to_vehicles:
        matched_vehicles = flat_to_vehicles[input_norm_flat]
        st.markdown(
            f"<h2 style='color:red; font-size:50px;'>Flat {input_norm_flat} के लिए Vehicle नंबर हैं: {', '.join(matched_vehicles)}</h2>",
            unsafe_allow_html=True,
        )

    else:
        st.markdown(
            "<h2 style='color:red; font-size:50px;'>..यह गाड़ी रिषभ टावर की वाहन सूची में नहीं है। शायद यह Reliance की हो सकती है या फिर कोई नई गाड़ी हो सकती है।<br>..गाड़ी के मालिक से फ्लैट नंबर पूछें या manager / supervisor से बात करें।</h2>",
            unsafe_allow_html=True,
        )
