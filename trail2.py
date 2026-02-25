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

# ========================
# SESSION STATE INIT
# ========================
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

# ============================
# HELPER FUNCTION
# ============================
def clean_name(name):
    name = name.upper().replace(".", "").replace("!", "").strip()
    for title in ["MR", "MISS"]:
        if name.startswith(title + " "):
            name = name[len(title)+1:]
    name = " ".join(name.split())
    return name

# =============================
# LOGIN PAGE ONLY
# =============================
if st.session_state.logged_in_user is None:

    hospital_image_url = "https://i.ibb.co/7NYqvcHz/hospital.jpg"
    st.image(hospital_image_url, width=400)

    st.markdown("<h2 style='color:purple;'>KDAH</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:green;'>Coded for CSSD Department</h4>", unsafe_allow_html=True)
    st.markdown("<p style='color:orange;'>Note: App is under consideration and development </p>", unsafe_allow_html=True)

    st.markdown("<h4 style='color:#444;'>Quote of the Moment</h4>", unsafe_allow_html=True)
    quote = get_random_quote()
    st.info(quote)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    mp3_files = [os.path.join(current_dir, f) for f in os.listdir(current_dir) if f.lower().endswith(".mp3")]

    if mp3_files:
        random_song = random.choice(mp3_files)
        with open(random_song, "rb") as f:
            audio_bytes = f.read()
        b64 = base64.b64encode(audio_bytes).decode()

        audio_html = f"""
        <audio>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
    else:
        st.warning("No mp3 files found in this folder")

    st.markdown("""
    <style>
    div.stButton > button[kind="primary"] {
        background-color: #28a745;
        color: white;
        font-size: 20px;
        font-weight: bold;
        padding: 0.6em 1.2em;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

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

# =============================
# AFTER LOGIN
# =============================
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

st.markdown(
    f"""
    <div style='background-color:#e8f5e9;padding:14px;border-radius:10px;text-align:center;margin-bottom:15px;'>
        <span style='color:#28a745;font-size:30px;font-weight:bold;'>
            {greeting}, {first_name}!
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

if st.button("Logout"):
    for key in defaults.keys():
        st.session_state[key] = None
    st.rerun()

# =============================
# OPTION SELECT PAGE
# =============================
if st.session_state.query_option is None:

    st.markdown("<h2 style='color:#FF5733; font-weight:bold;'>Select Option</h2>", unsafe_allow_html=True)

    choice = st.radio(
        "",
        [
            "Separate Pack",
            "Set",
            "ETO Query",
            "Plasma Query",
            "Autoclave Query",
            "5th Floor Handover",
            "3rd Floor Handover",
            "Set Identification"
        ]
    )

    if st.button("Continue", type="primary"):
        st.session_state.query_option = choice
        st.rerun()

    st.stop()

option = st.session_state.query_option

if st.button("⬅ Back"):
    st.session_state.query_option = None
    st.rerun()

# ==============================
# PLASMA QUERY SECTION
# ==============================
if option == "Plasma Query":

    import numpy as np
    import cv2
    from PIL import Image
    import requests
    from io import BytesIO

    st.markdown("## Plasma Sterilization Item Recognition")

    try:
        df_plasma = pd.read_csv("plasma.csv")
    except:
        st.error("plasma.csv not found.")
        st.stop()

    uploaded_file = st.file_uploader("Upload item photo", type=["png","jpg","jpeg"])
    camera_file = st.camera_input("Or take a photo")

    img_file = uploaded_file if uploaded_file else camera_file

    if img_file is not None:

        query_img = Image.open(img_file).convert("RGB").resize((400, 400))
        st.image(query_img, width=250)

        query_np = np.array(query_img)
        query_gray = cv2.cvtColor(query_np, cv2.COLOR_RGB2GRAY)

        orb = cv2.ORB_create(nfeatures=2000)
        kp1, des1 = orb.detectAndCompute(query_gray, None)

        if des1 is None:
            st.warning("Not enough features detected.")
            st.stop()

        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        query_hist = cv2.calcHist([query_np],[0,1,2],None,[8,8,8],[0,256,0,256,0,256])
        cv2.normalize(query_hist, query_hist)

        best_score = 0
        best_match = None
        matched_img = None

        for _, row in df_plasma.iterrows():

            drive_link = row["image_url"]

            if "/d/" in drive_link:
                file_id = drive_link.split("/d/")[1].split("/")[0]
                img_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            else:
                img_url = drive_link

            try:
                response = requests.get(img_url)
                item_img = Image.open(BytesIO(response.content)).convert("RGB").resize((400,400))
            except:
                continue

            item_np = np.array(item_img)
            item_gray = cv2.cvtColor(item_np, cv2.COLOR_RGB2GRAY)

            kp2, des2 = orb.detectAndCompute(item_gray, None)
            if des2 is None:
                continue

            matches = bf.match(des1, des2)
            match_count = len(matches)

            item_hist = cv2.calcHist([item_np],[0,1,2],None,[8,8,8],[0,256,0,256,0,256])
            cv2.normalize(item_hist, item_hist)

            color_score = cv2.compareHist(query_hist, item_hist, cv2.HISTCMP_CORREL)

            combined_score = (match_count * 0.6) + (color_score * 100 * 0.4)

            if combined_score > best_score:
                best_score = combined_score
                best_match = row["item_name"]
                matched_img = item_img

        if best_score > 30:
            st.success(f"Item Identified: {best_match}")
            st.image(matched_img, width=250)
        else:
            st.warning("No strong match found.")

else:
    st.info("Upcoming Feature")

# =============================
# ISSUE HISTORY
# =============================
st.subheader("Issue History")