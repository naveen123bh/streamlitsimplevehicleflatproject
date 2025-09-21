import sys
import os
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
    st.error(f"File not found: {default_file}")
    st.stop()

try:
    df = pd.read_excel(default_file)
    st.success(f"File '{default_file}' loaded successfully!")
except Exception as e:
    st.error(f"Error reading file '{default_file}': {e}")
    st.stop()  # stop further execution if file not found

# ===== Handle column mismatch =====
if df.shape[1] < 2:
    st.error("Excel file must have at least 2 columns: Vehicle and FlatNumber")
    st.stop()

# Keep only first two columns and rename
df = df.iloc[:, :2]
df.columns = ["Vehicle", "FlatNumber"]

# ===== Normalize columns =====
df["Vehicle"] = (
    df["Vehicle"]
    .astype(str)
    .str.upper()
    .str.strip()
    .str.replace("O", "0")  # replace letter O with zero
)
df["FlatNumber"] = df["FlatNumber"].astype(str).str.upper().str.strip()

# ===== Helper functions =====
def normalize_vehicle_input(vehicle_number):
    """Normalize vehicle number for case-insensitive lookup."""
    return str(vehicle_number).upper().strip().replace("O", "0")

def normalize_flat_input(flat_number):
    """Normalize flat number for consistent lookup."""
    return str(flat_number).upper().strip()

# ===== Unified Lookup GUI =====
user_input = st.text_input("Enter Vehicle Number or Flat Number")

if user_input:
    input_norm = user_input.strip().upper()
    
    # Check if input matches any Vehicle first
    vehicle_rows = df[df["Vehicle"] == normalize_vehicle_input(input_norm)]
    if not vehicle_rows.empty:
        flats = ", ".join(vehicle_rows["FlatNumber"].tolist())
        st.success(f"Flat number(s) for vehicle {input_norm}: {flats}")
    else:
        # Check if input matches any FlatNumber
        flat_rows = df[df["FlatNumber"] == normalize_flat_input(input_norm)]
        if not flat_rows.empty:
            vehicles = ", ".join(flat_rows["Vehicle"].tolist())
            st.success(f"Vehicle number(s) for flat {input_norm}: {vehicles}")
        else:
            st.error(f"No matching vehicle or flat number found for '{user_input}'")
