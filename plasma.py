import pandas as pd
import streamlit as st
import difflib
from datetime import datetime
import pytz
from PIL import Image
import os

# -----------------------------
# Plasma Section
# -----------------------------
def plasma_section():
    """
    Handles Plasma / Instrument Search and Inventory Display
    """

    # Load plasma CSV
    df = pd.read_csv("plasma.csv", engine="python", on_bad_lines="skip")
    df.columns = ["ItemName", "ImageURL"]
    df = df.apply(lambda x: x.astype(str).str.upper().str.strip())

    st.subheader("Plasma / Instrument Section")

    if "confirmed_item" not in st.session_state:
        st.session_state.confirmed_item = None

    if "similar_item_matches" not in st.session_state:
        st.session_state.similar_item_matches = None

    # -----------------------------
    # Search by Item Name
    # -----------------------------
    st.markdown("### Search by Item Name")

    item_input = st.text_input("Enter Item Name", key="plasma_text").upper().strip()

    if st.button("Search Item"):

        st.session_state.confirmed_item = None
        st.session_state.similar_item_matches = None

        exact = df[df["ItemName"] == item_input]

        if not exact.empty:
            st.session_state.confirmed_item = exact.iloc[0].to_dict()
        else:
            all_names = df["ItemName"].tolist()
            matches = difflib.get_close_matches(
                item_input,
                all_names,
                n=5,
                cutoff=0.4
            )
            if matches:
                st.session_state.similar_item_matches = matches
            else:
                st.error("No similar item found")

    # -----------------------------
    # Similar dropdown
    # -----------------------------
    if st.session_state.similar_item_matches:

        selected = st.selectbox(
            "Select Correct Item",
            st.session_state.similar_item_matches,
            key="selected_item_option"
        )

        if st.button("Confirm Item"):
            row = df[df["ItemName"] == selected].iloc[0]
            st.session_state.confirmed_item = row.to_dict()
            st.session_state.similar_item_matches = None

    # -----------------------------
    # Confirmed Item Display
    # -----------------------------
    if st.session_state.confirmed_item:
        data = st.session_state.confirmed_item
        st.success(f"Selected Item: {data['ItemName']}")

        # Display Image
        img_path = os.path.join("plasma_image", data['ImageURL'].lower())
        if os.path.exists(img_path):
            img = Image.open(img_path)
            st.image(img, width=300)
        else:
            st.warning("Image not found!")

    # -----------------------------
    # View Full Inventory
    # -----------------------------
    st.markdown("---")
    st.markdown("### View Full Plasma Inventory")
    if st.button("Show All Items"):
        for idx, row in df.iterrows():
            st.markdown(f"**{row['ItemName']}**")
            img_path = os.path.join("plasma_image", row['ImageURL'].lower())
            if os.path.exists(img_path):
                img = Image.open(img_path)
                st.image(img, width=200)
            else:
                st.warning(f"Image not found: {row['ImageURL']}")