import streamlit as st
import pandas as pd
from datetime import datetime
import os
import re
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

# Normalize vehicle numbers
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

# ===== Guard Authentication =====
guards = {
    "Naveen Kumar": "123456",
    "Rajeev Padwal": "654321"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_guard" not in st.session_state:
    st.session_state.current_guard = None

if not st.session_state.logged_in:
    st.markdown("### Guard Login 🔐")
    selected_guard = st.selectbox("Select your name", list(guards.keys()))
    password_input = st.text_input("Enter your 6-digit password", type="password")
    
    if st.button("Login"):
        if selected_guard in guards and password_input == guards[selected_guard]:
            st.session_state.logged_in = True
            st.session_state.current_guard = selected_guard
            st.success(f"Welcome {selected_guard}! You can now access the gate log.")
        else:
            st.error("❌ Incorrect password. Access denied.")
else:
    st.info(f"Logged in as: {st.session_state.current_guard}")

# ===== Main App =====
if st.session_state.logged_in:
    # ===== Session State =====
    for key in ["gate", "step", "vehicle_type", "vehicle_number", "flat_number", "description"]:
        if key not in st.session_state:
            st.session_state[key] = None

    # ===== Helper functions =====
    def get_log_file(gate):
        return os.path.join(log_folder, f"vehicle_log_gate{gate}.txt")

    def get_entry_number(log_file):
        if not os.path.exists(log_file):
            return 1
        with open(log_file, "r") as f:
            lines = f.readlines()
        return len([line for line in lines if "Entry No." in line]) + 1

    def log_entry(gate, guard_name, vehicle_type, vehicle_number, action):
        log_file = get_log_file(gate)
        vehicle_number_norm = normalize_vehicle_input(vehicle_number)
        flat_number = vehicle_flat_pairs.get(vehicle_number_norm, "Unknown Flat")
        time_now = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%I:%M:%S %p")
        entry_no = get_entry_number(log_file)

        log_line = (
            f"Entry No.{entry_no} | "
            f"🚪 Gate {gate} | "
            f"👤 Guard: {guard_name} | "
            f"🚘 Vehicle: {vehicle_type} | "
            f"🔢 Number: {vehicle_number_norm} | "
            f"🏠 Flat: {flat_number} | "
            f"📍 Action: {action} | "
            f"⏰ Time: {time_now}\n"
        )

        with open(log_file, "a") as f:
            f.write(log_line)
        return log_line

    def read_log(gate):
        log_file = get_log_file(gate)
        if not os.path.exists(log_file):
            return []
        with open(log_file, "r") as f:
            return f.readlines()

    def clear_log(gate):
        open(get_log_file(gate), "w").close()

    def generate_summary(gate):
        log_lines = read_log(gate)
        if not log_lines:
            return "कोई डेटा उपलब्ध नहीं है।"

        summary = {}
        for line in log_lines:
            parts = line.split("|")
            if len(parts) < 7:
                continue
            vehicle_type = parts[3].split(":")[1].strip()
            action = parts[6].split(":")[1].strip()
            summary.setdefault(vehicle_type, {"IN": 0, "OUT": 0})
            if action == "IN":
                summary[vehicle_type]["IN"] += 1
            elif action == "OUT":
                summary[vehicle_type]["OUT"] += 1

        summary_text = ""
        count = 1
        for vehicle, counts in summary.items():
            summary_text += (
                f"**No.{count} → {vehicle}**: आज कुल 🟢 {counts['IN']} {vehicle} अंदर आई और 🔴 {counts['OUT']} {vehicle} बाहर गई।\n\n"
            )
            count += 1
        return summary_text

    # ===== Streamlit UI =====
    st.markdown("<h1 style='color:blue; text-align:center;'>🚓 Rishabh Tower Vehicle Log</h1>", unsafe_allow_html=True)

    # Gate selection
    st.markdown("### Select Gate:")
    gate = st.radio("Choose Gate", [1, 2], horizontal=True)
    st.session_state.gate = gate

    # Action selection
    st.markdown("### Vehicle Action:")
    action = st.radio("Select Action", ["IN", "OUT"], horizontal=True)
    st.session_state.step = action

    # Vehicle details
    st.markdown("### Vehicle Details:")
    vehicle_type = st.selectbox("Vehicle Type", ["Car", "Bike", "Scooty", "Taxi", "EV"])
    vehicle_number = st.text_input("Enter Vehicle Number")

    # Submit Entry
    if st.button("Submit Entry", use_container_width=True):
        if vehicle_number:
            log_line = log_entry(gate, st.session_state.current_guard, vehicle_type, vehicle_number, action)
            st.success("✅ Entry logged successfully!")
            st.markdown(f"<p style='color:blue; font-size:18px;'>{log_line}</p>", unsafe_allow_html=True)
        else:
            st.error("⚠️ Please enter Vehicle Number")

    # Show Logs
    if st.button(f"📖 Show Logs Gate {gate}", use_container_width=True):
        log_data = read_log(gate)
        if log_data:
            for line in log_data:
                st.markdown(f"<p style='color:purple; font-size:16px;'>{line}</p>", unsafe_allow_html=True)
        else:
            st.info("No logs yet for this gate.")

    # Show Summary in Hindi
    if st.button(f"📊 Show Summary Gate {gate}", use_container_width=True):
        summary = generate_summary(gate)
        st.markdown(f"<div style='color:green; font-size:18px; font-weight:bold;'>{summary}</div>", unsafe_allow_html=True)

    # Clear Logs
    if st.button(f"🗑️ Clear Log Gate {gate}", use_container_width=True):
        clear_log(gate)
        st.warning(f"Logs for Gate {gate} cleared!")
