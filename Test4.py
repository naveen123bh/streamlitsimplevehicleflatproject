import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Folder to store logs
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)

# Mapping of vehicle numbers to flats (you can expand this list)
vehicle_to_flat = {
    "MH01EV9273": "F'DILIP PAANCHAL--1101",
    "MH02AB1234": "Flat 202",
    "MH03XY7890": "Flat 303"
}

# Function to get log file path for a given gate
def get_log_file(gate):
    return os.path.join(log_folder, f"vehicle_log_gate{gate}.txt")

# Function to count entries in log (for numbering)
def get_entry_number(log_file):
    if not os.path.exists(log_file):
        return 1
    with open(log_file, "r") as f:
        lines = f.readlines()
    return len([line for line in lines if "Entry No." in line]) + 1

# Function to log entry
def log_entry(gate, vehicle_type, vehicle_number, action):
    log_file = get_log_file(gate)
    flat_number = vehicle_to_flat.get(vehicle_number, "Unknown Flat")
    time_now = datetime.now().strftime("%I:%M:%S %p")  # 12-hour format
    entry_no = get_entry_number(log_file)

    log_line = (
        f"Entry No.{entry_no} | "
        f"🚪 Gate {gate} | "
        f"🚘 Vehicle: {vehicle_type} | "
        f"🔢 Number: {vehicle_number} | "
        f"🏠 Flat: {flat_number} | "
        f"📍 Action: {action} | "
        f"⏰ Time: {time_now}\n"
    )

    with open(log_file, "a") as f:
        f.write(log_line)

    return log_line

# Function to read log file
def read_log(gate):
    log_file = get_log_file(gate)
    if not os.path.exists(log_file):
        return []
    with open(log_file, "r") as f:
        return f.readlines()

# Function to clear log file
def clear_log(gate):
    log_file = get_log_file(gate)
    open(log_file, "w").close()

# Function to generate summary
def generate_summary(gate):
    log_lines = read_log(gate)
    if not log_lines:
        return "No data available."

    summary = {}
    for line in log_lines:
        parts = line.split("|")
        if len(parts) < 6:
            continue
        vehicle_type = parts[2].split(":")[1].strip()
        action = parts[5].split(":")[1].strip()
        summary.setdefault(vehicle_type, {"IN": 0, "OUT": 0})
        if action == "IN":
            summary[vehicle_type]["IN"] += 1
        elif action == "OUT":
            summary[vehicle_type]["OUT"] += 1

    # Format summary
    summary_text = ""
    count = 1
    for vehicle, counts in summary.items():
        summary_text += (
            f"**No.{count} → {vehicle}**: "
            f"🟢 IN = {counts['IN']} | 🔴 OUT = {counts['OUT']}\n\n"
        )
        count += 1
    return summary_text

# Streamlit UI
st.title("🚓 Vehicle Entry Management System")

st.markdown("### Select Gate:")
col1, col2 = st.columns(2)
with col1:
    gate = st.radio("Choose Gate", [1, 2], horizontal=True)

st.markdown("### Vehicle Action:")
action = st.radio("Select Action", ["IN", "OUT"], horizontal=True)

st.markdown("### Vehicle Details:")
vehicle_type = st.selectbox("Vehicle Type", ["Car", "Bike", "Scooty", "Taxi", "E.V"])
vehicle_number = st.text_input("Enter Vehicle Number")

if st.button("Submit Entry", use_container_width=True):
    if vehicle_number:
        log_line = log_entry(gate, vehicle_type, vehicle_number, action)
        st.success("Entry logged successfully!")
        st.markdown(f"<p style='color:blue; font-size:18px;'>{log_line}</p>", unsafe_allow_html=True)
    else:
        st.error("Please enter Vehicle Number")

# Show Logs
if st.button(f"📖 Show Logs Gate {gate}", use_container_width=True):
    log_data = read_log(gate)
    if log_data:
        for line in log_data:
            st.markdown(f"<p style='color:purple; font-size:16px;'>{line}</p>", unsafe_allow_html=True)
    else:
        st.info("No logs yet for this gate.")

# Show Summary
if st.button(f"📊 Show Summary Gate {gate}", use_container_width=True):
    summary = generate_summary(gate)
    st.markdown(f"<div style='color:green; font-size:18px; font-weight:bold;'>{summary}</div>", unsafe_allow_html=True)

# Clear Logs
if st.button(f"🗑️ Clear Log Gate {gate}", use_container_width=True):
    clear_log(gate)
    st.warning(f"Logs for Gate {gate} cleared!")
