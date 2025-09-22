import os
import re
import streamlit as st
import pandas as pd
from datetime import datetime
import pytz  # For India timezone

# ===== Setup internal folder for logs =====
log_folder = "vehicle_logs"
os.makedirs(log_folder, exist_ok=True)
log_file = os.path.join(log_folder, "vehicle_log.txt")

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

# ===== Show Log Option =====
if st.button("Show Vehicle Log"):
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            log_content = f.read()
        st.text_area("Vehicle Log", value=log_content, height=300)
    else:
        st.info("No log entries yet.")

# ===== Step 1: IN/OUT selection with attractive buttons =====
if st.session_state.step is None:
    st.markdown("<h3 style='color:green;'>Select Vehicle Movement</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.markdown('<button style="background-color:green;color:white;font-size:30px;padding:20px;width:100%;border-radius:10px;">IN</button>', unsafe_allow_html=True):
            if st.button("IN", key="in_click"):
                st.session_state.step = "IN"
    with col2:
        if st.markdown('<button style="background-color:red;color:white;font-size:30px;padding:20px;width:100%;border-radius:10px;">OUT</button>', unsafe_allow_html=True):
            if st.button("OUT", key="out_click"):
                st.session_state.step = "OUT"

# ===== Step 2: Vehicle Type Selection =====
elif st.session_state.step and st.session_state.vehicle_type is None:
    st.markdown(f"<h3 style='color:purple;'>Vehicle Type for {st.session_state.step}</h3>", unsafe_allow_html=True)
    vehicle_type = st.selectbox("Select vehicle type", ["Car", "Bike", "Scooty", "Taxi", "EV"])
    # Single click proceed immediately
    if vehicle_type:
        st.session_state.vehicle_type = vehicle_type

# ===== Step 3: Vehicle Number Input =====
elif st.session_state.vehicle_type and st.session_state.vehicle_number is None:
    st.markdown(f"<h3 style='color:purple;'>Enter Vehicle Number</h3>", unsafe_allow_html=True)
    vehicle_number_input = st.text_input("Vehicle Number", "")
    # Attractive Submit button
    submit_button = st.button("Submit Entry")
    if submit_button and vehicle_number_input.strip() != "":
        vehicle_number_norm = normalize_vehicle_input(vehicle_number_input)
        st.session_state.vehicle_number = vehicle_number_norm

        # Auto-map flat number
        st.session_state.flat_number = vehicle_flat_pairs.get(vehicle_number_norm, "Unknown Flat")

        # Capture current time in IST
        tz = pytz.timezone("Asia/Kolkata")
        current_time = datetime.now(tz).strftime("%H:%M:%S")  # Only time

        # Create description
        description = f"Vehicle {st.session_state.vehicle_number} of type {st.session_state.vehicle_type} {st.session_state.step} at {current_time} for Flat {st.session_state.flat_number}"
        st.session_state.description = description

        # Show description
        st.success(description)

        # Append to log file in internal folder
        with open(log_file, "a") as f:
            f.write(description + "\n")

        # Reset for next entry
        st.session_state.step = None
        st.session_state.vehicle_type = None
        st.session_state.vehicle_number = None
        st.session_state.flat_number = None
        st.session_state.description = None
