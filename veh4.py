#requirements.txt - streamlit==1.38.0
#pandas==2.2.2
#openpyxl==3.1.5

import streamlit as st
import pandas as pd

st.title("Vehicle ↔ Flat Number Lookup Tool")

# ===== File upload =====
uploaded_file = st.file_uploader("Upload your Excel file (.xlsx)", type="xlsx")

if uploaded_file is not None:
    try:
        # ===== Load Excel =====
        df = pd.read_excel(uploaded_file)
        st.success("File loaded successfully!")

        # ===== Normalize columns =====
        df.columns = ["Vehicle", "FlatNumber"]
        df["Vehicle"] = (
            df["Vehicle"]
            .astype(str)
            .str.upper()
            .str.strip()
            .str.replace("O", "0")  # replace letter O with zero
        )
        df["FlatNumber"] = df["FlatNumber"].astype(str).str.strip()

        # ===== Helper function =====
        def normalize_vehicle_input(vehicle_number):
            return vehicle_number.upper().strip().replace("O", "0")

        # ===== Lookup GUI =====
        lookup_type = st.radio("Choose lookup type", ["Vehicle → Flat", "Flat → Vehicle"])

        if lookup_type == "Vehicle → Flat":
            vehicle_number = st.text_input("Enter Vehicle Number")
            if vehicle_number:
                vehicle_number_norm = normalize_vehicle_input(vehicle_number)
                row = df[df["Vehicle"] == vehicle_number_norm]
                if not row.empty:
                    st.success(f"Flat number of {vehicle_number_norm} is {row['FlatNumber'].values[0]}")
                else:
                    st.error(f"Vehicle number {vehicle_number_norm} not found")

        else:  # Flat → Vehicle
            flat_number = st.text_input("Enter Flat Number")
            if flat_number:
                row = df[df["FlatNumber"] == flat_number.strip()]
                if not row.empty:
                    st.success(f"Vehicle number for flat {flat_number.strip()} is {row['Vehicle'].values[0]}")
                else:
                    st.error(f"Flat number {flat_number.strip()} not found")

    except Exception as e:
        st.error(f"Error reading file: {e}")
