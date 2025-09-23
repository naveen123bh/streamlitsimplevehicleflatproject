# ========================== Combined Vehicle Log + Voice Input App ==========================
import streamlit as st
import pandas as pd
from datetime import datetime
import os
import re
import pytz  # For India timezone
import tempfile
import numpy as np
import wavio
import whisper
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode

# ========================== Setup Folders and CSV ==========================
log_folder = "vehicle_logs"
os.makedirs(log_folder, exist_ok=True)

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

# ========================== Users ==========================
users = {
    # Guards
    "Naveen Kumar": "482915",
    "Rajeev Padwal": "736204",
    "Suresh Sagare": "591837",
    "Babban": "264905",
    "Manoj": "853192",
    "pramod": "670481",
    "Sandeep Karekar": "309572",
    # Supervisors
    "Satyam Kumar": "927364",
    "Sagar Bamne": "615283"
}

# ========================== Session State Initialization ==========================
if "logged_in_users" not in st.session_state:
    st.session_state.logged_in_users = []

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# ========================== Logging Functions ==========================
def get_log_file(gate):
    return os.path.join(log_folder, f"vehicle_log_gate{gate}.txt")

def get_entry_number(log_file):
    if not os.path.exists(log_file):
        return 1
    with open(log_file, "r") as f:
        lines = f.readlines()
    return len([line for line in lines if "Entry No." in line]) + 1

def log_entry(gate, user_name, vehicle_type, vehicle_number, action):
    log_file = get_log_file(gate)
    vehicle_number_norm = normalize_vehicle_input(vehicle_number)
    flat_number = vehicle_flat_pairs.get(vehicle_number_norm, "Unknown Flat")

    time_now = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%I:%M:%S %p")
    entry_no = get_entry_number(log_file)

    log_line = (
        f"Entry No.{entry_no} | "
        f"🚪 Gate {gate} | "
        f"👤 User: {user_name} | "
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

# ========================== Login Section ==========================
st.markdown("<h1 style='color:blue; text-align:center;'>🚓 Rishabh Tower Vehicle Log</h1>", unsafe_allow_html=True)

if st.session_state.current_user is None:
    st.markdown("### User Login 🔐")
    available_users = list(users.keys())
    selected_user = st.selectbox("Select your name", available_users)
    password_input = st.text_input("Enter your 6-digit password", type="password")

    if st.button("Login"):
        if selected_user in users and password_input == users[selected_user]:
            if len(st.session_state.logged_in_users) < 5:
                st.session_state.logged_in_users.append(selected_user)
                st.session_state.current_user = selected_user
                st.success(f"Welcome {selected_user}! You are logged in.")
            else:
                st.warning("⚠️ Maximum 5 users already logged in.")
        else:
            st.error("❌ Incorrect password. Access denied.")
else:
    st.info(f"Logged in as: {st.session_state.current_user}")

if st.session_state.logged_in_users:
    st.info(f"Currently logged-in users: {', '.join(st.session_state.logged_in_users)}")

for user in st.session_state.logged_in_users.copy():
    if st.button(f"🚪 Log Out {user}"):
        st.session_state.logged_in_users.remove(user)
        if st.session_state.current_user == user:
            st.session_state.current_user = None
        st.success(f"{user} logged out successfully.")

# ========================== Voice Input Section ==========================
st.markdown("### 🎤 Voice Input for Vehicle Logging")

# Load Whisper model
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("small")  # CPU-friendly

model = load_whisper_model()

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.recorded_frames = []

    def recv(self, frame):
        pcm = frame.to_ndarray()
        self.recorded_frames.append(pcm)
        return frame

webrtc_ctx = webrtc_streamer(
    key="voice-input",
    mode=WebRtcMode.SENDRECV,
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False},
    async_processing=True
)

if webrtc_ctx.state.playing:
    if st.button("Process Voice Input"):
        audio_processor = webrtc_ctx.audio_processor
        if audio_processor and audio_processor.recorded_frames:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                audio_data = np.concatenate(audio_processor.recorded_frames, axis=0)
                wavio.write(f.name, audio_data, 44100, sampwidth=2)
                audio_file = f.name

            result = model.transcribe(audio_file)
            text = result["text"].upper()
            st.success(f"📝 Recognized Text: {text}")

            # Parse vehicle info
            vehicle_type = None
            action = None
            vehicle_number = None

            for vt in ["CAR","BIKE","SCOOTY","TAXI","EV"]:
                if vt in text:
                    vehicle_type = vt
            for act in ["IN","OUT"]:
                if act in text:
                    action = act
            vehicle_number_pattern = r"[A-Z]{2}[0-9]{1,2}[A-Z]{0,2}[0-9]{1,4}"
            match = re.search(vehicle_number_pattern, text)
            if match:
                vehicle_number = match.group(0)

            if vehicle_type and vehicle_number and action:
                # Default gate selection if not chosen yet
                gate = st.radio("Select Gate for Voice Entry", [1,2])
                log_line = log_entry(gate, st.session_state.current_user, vehicle_type, vehicle_number, action)
                st.success(f"✅ Vehicle Logged Automatically: {log_line}")
            else:
                st.warning("⚠️ Could not parse all details. Try speaking clearly.")
        else:
            st.warning("⚠️ No audio detected. Please speak clearly.")

# ========================== Manual Vehicle Logging Section ==========================
# Keep your existing manual logging UI (vehicle type, number, action) here
# Example snippet:
guard_users = ["Naveen Kumar","Rajeev Padwal","Suresh Sagare","Babban","Manoj","Rajaram","Sandeep Karekar","pramod"]
logged_in_guards = [u for u in st.session_state.logged_in_users if u in guard_users]

if logged_in_guards:
    st.markdown("### Select Gate:")
    gate = st.radio("Choose Gate", [1, 2], horizontal=True)

    st.markdown("### Vehicle Action:")
    action = st.radio("Select Action", ["IN", "OUT"], horizontal=True)

    st.markdown("### Vehicle Details:")
    vehicle_type = st.selectbox("Vehicle Type", ["Car", "Bike", "Scooty", "Taxi", "EV"])
    vehicle_number = st.text_input("Enter Vehicle Number")

    if st.button("Submit Entry", use_container_width=True):
        if vehicle_number:
            for guard in logged_in_guards:
                log_line = log_entry(gate, guard, vehicle_type, vehicle_number, action)
                st.success(f"✅ Entry logged successfully by {guard}!")
                st.markdown(f"<p style='color:blue; font-size:18px;'>{log_line}</p>", unsafe_allow_html=True)

                if "Unknown Flat" in log_line:
                    st.markdown(
                        "<p style='color:red; font-size:18px;'>"
                        "Please note: ye vehicle Rishabh tower ki vehicle  list me nahi hai, "
                        "vehicle ke owner se flat number puchhe. "
                        "</p>",
                        unsafe_allow_html=True
                    )
        else:
            st.error("⚠️ Please enter Vehicle Number")

# ========================== Logs & Summary Section ==========================
for user in st.session_state.logged_in_users:
    st.markdown(f"### Logs & Summary for {user}")

    if user in guard_users:
        gate = st.radio(f"Select Gate for {user}", [1,2], key=f"gate_{user}")
    else:
        gate = st.radio(f"Select Gate for supervisor {user}", [1,2], key=f"gate_{user}")

    if st.button(f"📖 Show Logs Gate {gate} ({user})", key=f"showlog_{user}", use_container_width=True):
        log_data = read_log(gate)
        if log_data:
            for line in log_data:
                st.markdown(f"<p style='color:purple; font-size:16px;'>{line}</p>", unsafe_allow_html=True)
        else:
            st.info("No logs yet for this gate.")

    if st.button(f"📊 Show Summary Gate {gate} ({user})", key=f"summary_{user}", use_container_width=True):
        summary = generate_summary(gate)
        st.markdown(f"<div style='color:green; font-size:18px; font-weight:bold;'>{summary}</div>", unsafe_allow_html=True)

    if st.button(f"🗑️ Clear Log Gate {gate} ({user})", key=f"clear_{user}", use_container_width=True):
        if user == "Naveen Kumar":
            clear_log(gate)
            st.warning(f"Logs for Gate {gate} cleared by {user}!")
        else:
            st.error("❌ Only Naveen Kumar is authorized to clear logs.")
