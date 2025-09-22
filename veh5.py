import os
import re
import sys
import openpyxl
import streamlit as st
import pandas as pd

# ===== Python version check =====
st.write("Python version:", sys.version)
st.write("openpyxl version:", openpyxl.__version__)

st.title("Vehicle ↔ Flat Number Lookup Tool")

# ===== File setup =====
default_file = "vehnew.xlsx"  # relative path, file is in the same folder as your script

# Check if file exists
if not os.path.exists(default_file):
    st.error(f"फ़ाइल नहीं मिली: {default_file}")
    st.stop()

try:
    df = pd.read_excel(default_file)
    st.success(f"फ़ाइल '{default_file}' सफलतापूर्वक लोड हुई!")
except Exception as e:
    st.error(f"फ़ाइल पढ़ने में त्रुटि '{default_file}': {e}")
    st.stop()

# ===== Handle column mismatch =====
if df.shape[1] < 2:
    st.error("Excel फ़ाइल में कम से कम 2 कॉलम होने चाहिए: Vehicle और FlatNumber")
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

# ===== Unified Lookup GUI =====
user_input = st.text_input("Vehicle Number या Flat Number दर्ज करें")

if user_input:
    input_norm_vehicle = normalize_vehicle_input(user_input)
    input_norm_flat = normalize_flat_input(user_input)

    # Check if input matches any Vehicle
    vehicle_rows = df[df["Vehicle"] == input_norm_vehicle]
    if not vehicle_rows.empty:
        flats = ", ".join(vehicle_rows["FlatNumber"].tolist())
        st.success(f"Vehicle {input_norm_vehicle} का Flat number(s): {flats}")
    else:
        # Check if input matches any FlatNumber
        flat_rows = df[df["FlatNumber"] == input_norm_flat]
        if not flat_rows.empty:
            vehicles = ", ".join(flat_rows["Vehicle"].tolist())
            st.success(f"Flat {input_norm_flat} का Vehicle number(s): {vehicles}")
        else:
            # Updated friendly Hindi message for no match (reordered)
            st.warning(
                "वाहन सूची अपडेट की जा रही है। कार्य प्रगति में है।\n"
                "कृपया 2 दिन प्रतीक्षा करें: लेखक इस पर काम कर रहे हैं।"
            )
