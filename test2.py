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
"  # <-- put your Excel file path here

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
    return vehicle_number.upper().strip().replace("O", "0")

def normalize_flat_input(flat_number):
    return flat_number.upper().strip()

# ===== Lookup GUI =====
lookup_type = st.radio("Choose lookup type", ["Vehicle → Flat", "Flat → Vehicle"])

if lookup_type == "Vehicle → Flat":
    vehicle_number = st.text_input("Enter Vehicle Number")
    if vehicle_number:
        vehicle_number_norm = normalize_vehicle_input(vehicle_number)
        rows = df[df["Vehicle"] == vehicle_number_norm]
        if not rows.empty:
            flats = ", ".join(rows["FlatNumber"].tolist())
            st.success(f"Flat number(s) for vehicle {vehicle_number_norm}: {flats}")
        else:
            st.error(f"Vehicle number {vehicle_number_norm} not found")

else:  # Flat → Vehicle
    flat_number = st.text_input("Enter Flat Number")
    if flat_number:
        flat_number_norm = normalize_flat_input(flat_number)
        rows = df[df["FlatNumber"] == flat_number_norm]
        if not rows.empty:
            vehicles = ", ".join(rows["Vehicle"].tolist())
            st.success(f"Vehicle number(s) for flat {flat_number_norm}: {vehicles}")
        else:
            st.error(f"Flat number {flat_number_norm} not found")
