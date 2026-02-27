import pandas as pd
import streamlit as st
from PIL import Image
import os
import difflib
import math

def plasma_section():
    """
    Plasma / Instrument Recognition with Search + Confirm + Paginated Inventory
    """

    # Load CSv
    df = pd.read_csv("plasma.csv", engine="python", on_bad_lines="skip")
    df.columns = ["ItemName", "ImageFile"]
    df = df.apply(lambda x: x.astype(str).str.upper().str.strip())

    st.subheader("Plasma / Instrument Section")

    # Initialize session states
    if "confirmed_item" not in st.session_state:
        st.session_state.confirmed_item = None
    if "similar_item_matches" not in st.session_state:
        st.session_state.similar_item_matches = None
    if "plasma_inventory_page" not in st.session_state:
        st.session_state.plasma_inventory_page = 1

    # -----------------------------
    # Search Input
    # -----------------------------
    item_input = st.text_input("Enter Item Name", key="plasma_text").upper().strip()

    if st.button("Search Item") or item_input:
        st.session_state.confirmed_item = None
        st.session_state.similar_item_matches = None

        # Exact match
        exact = df[df["ItemName"] == item_input]
        if not exact.empty:
            st.session_state.confirmed_item = exact.iloc[0].to_dict()
        else:
            # Close matches
            matches = difflib.get_close_matches(item_input, df["ItemName"].tolist(), n=5, cutoff=0.4)
            if matches:
                st.session_state.similar_item_matches = matches
            else:
                st.warning("No exact or close match found!")

    # -----------------------------
    # Similar Dropdown
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
    # Display Confirmed Item
    # -----------------------------
    if st.session_state.confirmed_item:
        data = st.session_state.confirmed_item
        st.success(f"Selected Item: {data['ItemName']}")
        img_path = os.path.join("plasma_image", data['ImageFile'])
        if os.path.exists(img_path):
            img = Image.open(img_path)
            st.image(img, width=300)
        else:
            st.warning(f"Image not found: {data['ImageFile']}")

    # -----------------------------
    # Full Inventory with Pagination
    # -----------------------------
    st.markdown("---")
    st.markdown("### View Full Plasma Inventory (Paginated)")

    items_per_page = 10
    total_items = len(df)
    total_pages = math.ceil(total_items / items_per_page)
    page = st.session_state.plasma_inventory_page

    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_items = df.iloc[start_idx:end_idx]

    for _, row in page_items.iterrows():
        st.markdown(f"**{row['ItemName']}**")
        img_path = os.path.join("plasma_image", row['ImageFile'])
        if os.path.exists(img_path):
            img = Image.open(img_path)
            st.image(img, width=200)
        else:
            st.warning(f"Image not found: {row['ImageFile']}")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅ Previous") and page > 1:
            st.session_state.plasma_inventory_page -= 1
            st.experimental_rerun()
    with col3:
        if st.button("Next ➡") and page < total_pages:
            st.session_state.plasma_inventory_page += 1
            st.experimental_rerun()
    with col2:
        st.markdown(f"Page {page} of {total_pages}")