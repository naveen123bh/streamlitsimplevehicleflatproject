import os
import re
import sys
import openpyxl
import streamlit as st
import pandas as pd

# ===== Heading =====
st.markdown("<h1 style='text-align:center; color:#FF5733; font-size:70px;'>Rishabh Tower Security</h1>", unsafe_allow_html=True)

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

# ===== Input =====
st.markdown("<h1 style='text-align:center; color:#D35400; font-size:60px;'>Vehicle या Flat Number डालें</h1>", unsafe_allow_html=True)
user_input = st.text_input("", "", key="user_input")

# ===== Button =====
if st.button("Result देखें", key="result_button"):
    if user_input:
        input_norm_vehicle = normalize_vehicle_input(user_input)
        input_norm_flat = normalize_flat_input(user_input)

        vehicle_rows = df[df["Vehicle"] == input_norm_vehicle]
        if not vehicle_rows.empty:
            flats = ", ".join(vehicle_rows["FlatNumber"].tolist())
            st.markdown(f"<h1 style='text-align:center; color:#196F3D; font-size:60px;'>Vehicle {input_norm_vehicle} का Flat number(s): {flats}</h1>", unsafe_allow_html=True)
        else:
            flat_rows = df[df["FlatNumber"] == input_norm_flat]
            if not flat_rows.empty:
                vehicles = ", ".join(flat_rows["Vehicle"].tolist())
                st.markdown(f"<h1 style='text-align:center; color:#196F3D; font-size:60px;'>Flat {input_norm_flat} का Vehicle number(s): {vehicles}</h1>", unsafe_allow_html=True)
            else:
                st.markdown("<h1 style='text-align:center; color:#CB4335; font-size:60px;'>वाहन सूची अपडेट की जा रही है। कार्य प्रगति में है।<br>कृपया 2 दिन प्रतीक्षा करें: लेखक इस पर काम कर रहे हैं।</h1>", unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='text-align:center; color:#CB4335; font-size:60px;'>कृपया Vehicle या Flat Number दर्ज करें।</h1>", unsafe_allow_html=True)
