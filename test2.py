import os
import re
import streamlit as st
import pandas as pd
from datetime import datetime

# ===== Load vehicle-flat mapping =====
raw_file = "vehicle_flat_pairs.csv"
if not os.path.exists(raw_file):
    st.error(f"File not found: {raw_file}")
    st.stop()

df = pd.read_csv(raw_file)
df = df.iloc[:, :2]
df.columns = ["Vehicle", "FlatNumber"]

def normalize_vehicle_input(vehicle_number):
    if pd.isna(vehicle_number) or vehicle_number=="":
        return ""
    text = str(vehicle_number).upper()
    text = re.sub(r"\s+", "", text)
    text = text.replace("O", "0")
    return text.strip()

df["Vehicle"] = df["Vehicle"].apply(normalize_vehicle_input)
df["FlatNumber"] = df["FlatNumber"].apply(lambda x: str(x).upper())
vehicle_flat_pairs = dict(zip(df["Vehicle"], df["FlatNumber"]))

# ===== Session State =====
if "step" not in st.session_state:
    st.session_state.step = None  # IN / OUT
if "vehicle_type" not in st.session_state:
    st.session_state.vehicle_type = None
if "vehicle_number" not in st.session_state:
    st.session_state.vehicle_number = None
if "flat_number" not in st.session_state:
    st.session_state.flat_number = None
if "description" not in st.session_state:
    st.session_state.description = None

# ===== App Heading =====
st.markdown("<h1 style='color:blue; font-size:50px;'>Rishabh Tower Vehicle Log</h1>", unsafe_allow_html=True)

# ===== Step 1: IN/OUT selection =====
if st.session_state.step is None:
    st.markdown("<h3 style='color:green;'>Select Vehicle Movement</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("IN"):
            st.session_state.step = "IN"
    with col2:
        if st.button("OUT"):
            st.session_state.step = "OUT"

# ===== Step 2: Vehicle Type Selection =====
elif st.session_state.step and st.session_state.vehicle_type is None:
    st.markdown(f"<h3 style='color:purple;'>Vehicle Type for {st.session_state.step}</h3>", unsafe_allow_html=True)
    vehicle_type = st.selectbox("Select vehicle type", ["Car", "Bike", "Scooty", "Taxi", "EV"])
    if st.button("Next: Vehicle Number"):
        st.session_state.vehicle_type = vehicle_type

# ===== Step 3: Vehicle Number Input =====
elif st.session_state.vehicle_type and st.session_state.vehicle_number is None:
    st.markdown(f"<h3 style='color:purple;'>Enter Vehicle Number</h3>", unsafe_allow_html=True)
    vehicle_number_input = st.text_input("Vehicle Number", "")
    if st.button("Submit Entry"):
        vehicle_number_norm = normalize_vehicle_input(vehicle_number_input)
        st.session_state.vehicle_number = vehicle_number_norm

        # Auto-map flat number
        st.session_state.flat_number = vehicle_flat_pairs.get(vehicle_number_norm, "Unknown Flat")

        # Capture current time
        current_time = datetime.now().strftime("%H:%M:%S")

        # Create description
        description = f"Vehicle {st.session_state.vehicle_number} of type {st.session_state.vehicle_type} {st.session_state.step} at {current_time} for Flat {st.session_state.flat_number}"
        st.session_state.description = description

        # Show description
        st.success(description)

        # Append to log file
        log_file = "vehicle_log.txt"
        with open(log_file, "a") as f:
            f.write(description + "\n")

        # Reset for next entry
        st.session_state.step = None
        st.session_state.vehicle_type = None
        st.session_state.vehicle_number = None
        st.session_state.flat_number = None
        st.session_state.description = None
