# this code is programmed by naveen123
import os
import random
import base64
import streamlit as st
import pandas as pd
import difflib
from technician import TECHNICIAN_NAMES
from sapset import search_and_issue_sets
from datetime import datetime
import pytz
from quotes import get_random_quote

# ============================
# SESSION STATE INIT
# =============================
defaults = {
    "logged_in_user": None,
    "login_selected_name": None,
    "query_option": None,
    "found_pack": None,
    "found_set": None
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ==============================
# HELPER FUNCTION
# ==============================
def clean_name(name):
    name = name.upper().replace(".", "").replace("!", "").strip()
    for title in ["MR", "MISS"]:
        if name.startswith(title + " "):
            name = name[len(title)+1:]
    name = " ".join(name.split())
    return name

# ==============================
# LOGIN PAGE ONLY
# ==============================
if st.session_state.logged_in_user is None:

    hospital_image_url = "https://i.ibb.co/7NYqvcHz/hospital.jpg"
    st.image(hospital_image_url, width=400)

    st.markdown("<h2 style='color:purple;'>KDAH</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:green;'>Coded for CSSD Department</h4>", unsafe_allow_html=True)
    st.markdown("<p style='color:orange;'>Note: App is under consideration and development </p>", unsafe_allow_html=True)

    st.markdown("<h4 style='color:#444;'>Quote of the Moment</h4>", unsafe_allow_html=True)
    quote = get_random_quote()
    st.info(quote)

    # ==============================
    # STRONGEST POSSIBLE AUTOPLAY
    # ==============================

    current_dir = os.path.dirname(os.path.abspath(__file__))

    mp3_files = [
        os.path.join(current_dir, f)
        for f in os.listdir(current_dir)
        if f.lower().endswith(".mp3")
    ]

    if mp3_files:
        random_song = random.choice(mp3_files)

        with open(random_song, "rb") as f:
            audio_bytes = f.read()

        b64 = base64.b64encode(audio_bytes).decode()

        audio_html = f"""
        <audio id="bgmusic" autoplay muted playsinline>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>

        <script>
        var audio = document.getElementById("bgmusic");

        // ensure autoplay attempt
        audio.play().catch(()=>{{}});

        // unmute on first user interaction
        function unmuteAudio() {{
            audio.muted = false;
            audio.play();
            document.removeEventListener("click", unmuteAudio);
            document.removeEventListener("touchstart", unmuteAudio);
        }}

        document.addEventListener("click", unmuteAudio);
        document.addEventListener("touchstart", unmuteAudio);
        </script>
        """

        st.markdown(audio_html, unsafe_allow_html=True)

    else:
        st.warning("No mp3 files found in this folder")

    # ==============================

    name_input = st.text_input("Technician Name")

    if name_input:
        cleaned_input = clean_name(name_input)
        normalized = {clean_name(n): n for n in TECHNICIAN_NAMES}

        if cleaned_input in normalized:
            st.session_state.login_selected_name = normalized[cleaned_input]
        else:
            suggestions = difflib.get_close_matches(cleaned_input, normalized.keys(), n=5, cutoff=0.5)
            if suggestions:
                options = [normalized[s] for s in suggestions]
                st.session_state.login_selected_name = st.selectbox("Did you mean:", options)

    if st.button("Login", type="primary"):
        if st.session_state.login_selected_name:
            st.session_state.logged_in_user = st.session_state.login_selected_name
            st.rerun()
        else:
            st.warning("Enter correct name")

    st.stop()

# ==============================
# AFTER LOGIN
# ==============================

ist = pytz.timezone("Asia/Kolkata")
now = datetime.now(ist)
current_hour = now.hour

if 4 <= current_hour < 12:
    greeting = "Good Morning"
elif 12 <= current_hour < 16:
    greeting = "Good Afternoon"
elif 16 <= current_hour < 21:
    greeting = "Good Evening"
else:
    greeting = "Hello"

full_name_parts = st.session_state.logged_in_user.strip().replace(".", "").split()
first_name = next((p.title() for p in full_name_parts if p.upper() not in ["MR", "MISS"]), full_name_parts[0].title())

st.success(f"{greeting}, {first_name}!")
