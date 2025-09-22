import os
import re
import streamlit as st
import pandas as pd
from datetime import datetime
import pytz  # For India timezone

# ===== Setup internal folder for logs =====
log_folder = "vehicle_logs"
os.makedirs(log_folder, exist_ok=True)

# ===== Load vehicle-flat mapping =====
raw_file = "vehicle_flat_pairs.csv"
if not os.path.exists(raw_file):
    st.error(f"File not found: {raw_file}")
    st.stop()

df = pd.read_csv(raw_file)
df = df.iloc[:, :2]
df.columns = ["Vehicle", "FlatNumber"]

def normalize_vehicle_input(vehicle_number):
    if pd.isna(vehicle_number) or vehicle_number == "":
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
    st.session_state.step = None
if "vehicle_type" not in st.session_state:
    st.session_state.vehicle_type = None
if "vehicle_number" not in st.session_state:
    st.session_state.vehicle_number = None
if "flat_number" not in st.session_state:
    st.session_state.flat_number = None
if "description" not in st.session_state:
    st.session_state.description = None
if "gate" not in st.session_state:
    st.session_state.gate = None

# ===== App Heading =====
st.markdown("<h1 style='color:blue; font-size:50px;'>Rishabh Tower Vehicle Log</h1>", unsafe_allow_html=True)

# ===== Gate Selection =====
if st.session_state.gate is None:
    st.markdown("<h3 style='color:green;'>Select Your Gate</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚪 Gate 1", key="gate1_btn"):
            st.session_state.gate = "Gate1"
    with col2:
        if st.button("🚪 Gate 2", key="gate2_btn"):
            st.session_state.gate = "Gate2"

    # Style buttons
    st.markdown(
        """
        <style>
        div[data-testid='stButton'] button[kind='primary'][key='gate1_btn'] {
            background-color: green !important;
            color: white !important;
            font-size: 24px !important;
            padding: 14px 28px !important;
            border-radius: 12px !important;
        }
        div[data-testid='stButton'] button[kind='primary'][key='gate2_btn'] {
            background-color: red !important;
            color: white !important;
            font-size: 24px !important;
            padding: 14px 28px !important;
            border-radius: 12px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ===== After gate selected =====
if st.session_state.gate:
    log_file = os.path.join(log_folder, f"vehicle_log_{st.session_state.gate}.txt")

    st.markdown(f"<h2 style='color:purple;'>You are logging from {st.session_state.gate}</h2>", unsafe_allow_html=True)

    # ===== Show & Clear Log Buttons per gate =====
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📘 Show Vehicle Log", key="show_log"):
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    log_content = f.read()
                st.text_area("Vehicle Log", value=log_content, height=300)
            else:
                st.info("No log entries yet.")
        st.markdown(
            "<style> div[data-testid='stButton'] button[kind='primary'][key='show_log'] {background-color: blue; color: white; font-size: 22px; padding: 12px 24px; border-radius: 12px;} </style>",
            unsafe_allow_html=True,
        )

    with col2:
        if st.button("🗑️ Clear Vehicle Log", key="clear_log"):
            with open(log_file, "w") as f:
                f.write("")
            st.success(f"{st.session_state.gate} log cleared successfully!")
        st.markdown(
            "<style> div[data-testid='stButton'] button[kind='primary'][key='clear_log'] {background-color: red; color: white; font-size: 22px; padding: 12px 24px; border-radius: 12px;} </style>",
            unsafe_allow_html=True,
        )

    # ===== Step 1: IN/OUT selection =====
    if st.session_state.step is None:
        st.markdown("<h3 style='color:green;'>Select Vehicle Movement</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ IN", key="in_btn"):
                st.session_state.step = "IN"
        with col2:
            if st.button("❌ OUT", key="out_btn"):
                st.session_state.step = "OUT"

        st.markdown(
            """
            <style>
            div[data-testid='stButton'] button[kind='primary'][key='in_btn'] {
                background-color: green !important;
                color: white !important;
                font-size: 28px !important;
                padding: 16px 32px !important;
                border-radius: 15px !important;
            }
            div[data-testid='stButton'] button[kind='primary'][key='out_btn'] {
                background-color: red !important;
                color: white !important;
                font-size: 28px !important;
                padding: 16px 32px !important;
                border-radius: 15px !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

    # ===== Step 2: Vehicle Type Selection =====
    elif st.session_state.step and st.session_state.vehicle_type is None:
        st.markdown(f"<h3 style='color:purple;'>Vehicle Type for {st.session_state.step}</h3>", unsafe_allow_html=True)
        vehicle_type = st.selectbox("Select vehicle type", ["Car", "Bike", "Scooty", "Taxi", "EV"])
        if vehicle_type:
            st.session_state.vehicle_type = vehicle_type

    # ===== Step 3: Vehicle Number Input =====
    elif st.session_state.vehicle_type and st.session_state.vehicle_number is None:
        st.markdown(f"<h3 style='color:orange;'>Enter Vehicle Number</h3>", unsafe_allow_html=True)
        vehicle_number_input = st.text_input("Vehicle Number", "")

        if st.button("Submit Entry", key="submit_vehicle"):
            vehicle_number_norm = normalize_vehicle_input(vehicle_number_input)
            st.session_state.vehicle_number = vehicle_number_norm

            # Auto-map flat number
            st.session_state.flat_number = vehicle_flat_pairs.get(vehicle_number_norm, "Unknown Flat")

            # Capture current time in IST
            tz = pytz.timezone("Asia/Kolkata")
            current_time = datetime.now(tz).strftime("%H:%M:%S")

            # Create description
            description = f"[{st.session_state.gate}] Vehicle {st.session_state.vehicle_number} of type {st.session_state.vehicle_type} {st.session_state.step} at {current_time} for Flat {st.session_state.flat_number}"
            st.session_state.description = description

            # Show description
            st.success(description)

            # Append to gate-specific log file
            with open(log_file, "a") as f:
                f.write(description + "\n")

            # Reset for next entry
            st.session_state.step = None
            st.session_state.vehicle_type = None
            st.session_state.vehicle_number = None
            st.session_state.flat_number = None
            st.session_state.description = None

        st.markdown(
            "<style> div[data-testid='stButton'] button[kind='primary'][key='submit_vehicle'] {background-color: orange; color: black; font-size: 24px; padding: 14px 28px; border-radius: 12px;} </style>",
            unsafe_allow_html=True,
        )
