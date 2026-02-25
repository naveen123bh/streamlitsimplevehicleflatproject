# =========================
# IMPORTS
# =========================
import os
import random
import base64
import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# Image Recognition Imports
import numpy as np
import cv2
from PIL import Image
import requests
from io import BytesIO


# =========================
# SESSION STATE
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "query_option" not in st.session_state:
    st.session_state.query_option = None


# =========================
# LOGIN PAGE
# =========================
if not st.session_state.logged_in:

    st.title("KDAH - CSSD Department")
    st.info("Plasma & Item Recognition System")

    name = st.text_input("Enter Technician Name")

    if st.button("Login"):
        if name.strip() != "":
            st.session_state.logged_in = True
            st.session_state.username = name
            st.rerun()
        else:
            st.warning("Enter your name")

    st.stop()


# =========================
# AFTER LOGIN
# =========================
ist = pytz.timezone("Asia/Kolkata")
now = datetime.now(ist)
hour = now.hour

if 4 <= hour < 12:
    greet = "Good Morning"
elif 12 <= hour < 17:
    greet = "Good Afternoon"
else:
    greet = "Good Evening"

st.success(f"{greet}, {st.session_state.username}")

if st.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.query_option = None
    st.rerun()


# =========================
# OPTION PAGE
# =========================
if st.session_state.query_option is None:

    choice = st.radio(
        "Select Option",
        ["Plasma Query", "ETO Query"]
    )

    if st.button("Continue"):
        st.session_state.query_option = choice
        st.rerun()

    st.stop()


# =========================
# BACK BUTTON
# =========================
if st.button("⬅ Back"):
    st.session_state.query_option = None
    st.rerun()


# =========================
# PLASMA QUERY
# =========================
if st.session_state.query_option == "Plasma Query":

    st.header("Plasma Sterilization Item Recognition")

    try:
        df = pd.read_csv("plasma.csv")
    except:
        st.error("plasma.csv not found in folder.")
        st.stop()

    uploaded_file = st.file_uploader("Upload item image", type=["jpg", "png", "jpeg"])
    camera_file = st.camera_input("Or Take Photo")

    img_file = uploaded_file if uploaded_file else camera_file

    if img_file is not None:

        # Prepare Query Image
        query_img = Image.open(img_file).convert("RGB").resize((400, 400))
        st.image(query_img, width=250)

        query_np = np.array(query_img)
        query_gray = cv2.cvtColor(query_np, cv2.COLOR_RGB2GRAY)

        # ORB Detector
        orb = cv2.ORB_create(nfeatures=2500)
        kp1, des1 = orb.detectAndCompute(query_gray, None)

        if des1 is None:
            st.warning("Not enough features found.")
            st.stop()

        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        # HSV Histogram (Color Matching)
        query_hsv = cv2.cvtColor(query_np, cv2.COLOR_RGB2HSV)
        query_hist = cv2.calcHist(
            [query_hsv],
            [0, 1],
            None,
            [50, 60],
            [0, 180, 0, 256]
        )
        cv2.normalize(query_hist, query_hist)

        best_score = 0
        best_match = None
        best_image = None

        # Compare with database images
        for _, row in df.iterrows():

            img_url = row["image_url"]

            try:
                response = requests.get(img_url, timeout=10)
                item_img = Image.open(BytesIO(response.content)).convert("RGB").resize((400, 400))
            except:
                continue

            item_np = np.array(item_img)
            item_gray = cv2.cvtColor(item_np, cv2.COLOR_RGB2GRAY)

            kp2, des2 = orb.detectAndCompute(item_gray, None)
            if des2 is None:
                continue

            matches = bf.match(des1, des2)
            match_count = len(matches)

            # HSV Histogram
            item_hsv = cv2.cvtColor(item_np, cv2.COLOR_RGB2HSV)
            item_hist = cv2.calcHist(
                [item_hsv],
                [0, 1],
                None,
                [50, 60],
                [0, 180, 0, 256]
            )
            cv2.normalize(item_hist, item_hist)

            color_score = cv2.compareHist(query_hist, item_hist, cv2.HISTCMP_CORREL)

            # Final Score
            combined_score = (match_count * 0.3) + (color_score * 100 * 0.7)

            if combined_score > best_score:
                best_score = combined_score
                best_match = row["item_name"]
                best_image = item_img

        # Result
        if best_score > 20:
            st.success(f"Item Identified: {best_match}")
            st.image(best_image, width=250)
            st.write(f"Score: {round(best_score,2)}")
        else:
            st.warning("No strong match found.")


# =========================
# ETO PLACEHOLDER
# =========================
if st.session_state.query_option == "ETO Query":
    st.info("ETO Query Feature Coming Soon")