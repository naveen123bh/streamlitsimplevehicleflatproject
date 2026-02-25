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
import csv
import requests
from PIL import Image
from io import BytesIO

# NEW IMPORTS
import cv2
import numpy as np

# =======================
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

# =============================
# HELPER FUNCTION
# =============================
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
st.title("CSSD Application")

if st.button("Logout"):
    for key in defaults.keys():
        st.session_state[key] = None
    st.rerun()

# =============================
# OPTION SELECT PAGE
# =============================
if st.session_state.query_option is None:

    choice = st.radio(
        "Select Option",
        [
            "Separate Pack",
            "Set",
            "Plasma Query"
        ]
    )

    if st.button("Continue"):
        st.session_state.query_option = choice
        st.rerun()

    st.stop()

option = st.session_state.query_option

if st.button("⬅ Back"):
    st.session_state.query_option = None
    st.rerun()

# ==============================
# PLASMA QUERY SECTION (ORB + COLOR)
# ==============================
if option == "Plasma Query":

    st.markdown("## Plasma Sterilization Item Recognition")

    try:
        df_plasma = pd.read_csv("plasma.csv")
    except:
        st.error("plasma.csv not found in project folder.")
        st.stop()

    uploaded_file = st.file_uploader("Upload item photo", type=["png","jpg","jpeg"])
    camera_file = st.camera_input("Or take a photo")

    img_file = uploaded_file if uploaded_file else camera_file

    if img_file is not None:

        query_img = Image.open(img_file).convert("RGB")
        st.image(query_img, caption="Uploaded Image", width=250)

        query_np = np.array(query_img)
        query_gray = cv2.cvtColor(query_np, cv2.COLOR_RGB2GRAY)

        orb = cv2.ORB_create(nfeatures=1000)
        kp1, des1 = orb.detectAndCompute(query_gray, None)

        if des1 is None:
            st.warning("Not enough features detected.")
            st.stop()

        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        # COLOR HISTOGRAM OF QUERY
        query_hist = cv2.calcHist([query_np], [0,1,2], None, [8,8,8], [0,256,0,256,0,256])
        cv2.normalize(query_hist, query_hist)

        best_match = None
        max_matches = 0
        best_color_score = 0
        matched_item_img = None

        for _, row in df_plasma.iterrows():

            drive_link = row["image_url"]

            if "/d/" in drive_link:
                file_id = drive_link.split("/d/")[1].split("/")[0]
                img_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            else:
                img_url = drive_link

            try:
                response_img = requests.get(img_url)
                item_img = Image.open(BytesIO(response_img.content)).convert("RGB")
            except:
                continue

            item_np = np.array(item_img)
            item_gray = cv2.cvtColor(item_np, cv2.COLOR_RGB2GRAY)

            kp2, des2 = orb.detectAndCompute(item_gray, None)
            if des2 is None:
                continue

            matches = bf.match(des1, des2)
            match_count = len(matches)

            # COLOR HISTOGRAM MATCH
            item_hist = cv2.calcHist([item_np], [0,1,2], None, [8,8,8], [0,256,0,256,0,256])
            cv2.normalize(item_hist, item_hist)

            color_score = cv2.compareHist(query_hist, item_hist, cv2.HISTCMP_CORREL)

            if match_count > max_matches and color_score > best_color_score:
                max_matches = match_count
                best_color_score = color_score
                best_match = row["item_name"]
                matched_item_img = item_img

        if max_matches > 15 and best_color_score > 0.7:
            st.success(f"Item Identified: {best_match}")
            st.image(matched_item_img, caption="Matched Image", width=250)
            st.info(f"Feature Matches: {max_matches} | Color Score: {round(best_color_score,2)}")
        else:
            st.warning("No strong match found. Try clearer image.")