# plasma.py
import streamlit as st
import pandas as pd
import difflib
import os

def plasma_section():
    # ----------------------------
    # Load plasma CSV
    # ----------------------------
    PLASMA_CSV = "plasma.csv"
    IMAGE_FOLDER = "plasma_images"

    if not os.path.exists(PLASMA_CSV):
        st.error(f"{PLASMA_CSV} not found!")
        return

    df = pd.read_csv(PLASMA_CSV, engine="python", on_bad_lines="skip")
    df.columns = ["ItemName", "ImageFile"]
    df["ItemName"] = df["ItemName"].str.upper().str.strip()

    st.subheader("Plasma /autocoave Instrument Section")

    # -----------------------------
    # Search by Name
    # -----------------------------
    search_input = st.text_input("Enter Item Name to Search").upper().strip()
    confirmed_item = None

    if st.button("Search Item"):
        if search_input:
            exact = df[df["ItemName"] == search_input]
            if not exact.empty:
                confirmed_item = exact.iloc[0]
            else:
                matches = difflib.get_close_matches(
                    search_input, df["ItemName"].tolist(), n=5, cutoff=0.4
                )
                if matches:
                    selected_name = st.selectbox("Did you mean:", matches)
                    if selected_name:
                        confirmed_item = df[df["ItemName"] == selected_name].iloc[0]

    # -----------------------------
    # Show Selected Item
    # -----------------------------
    if confirmed_item is not None:
        st.markdown(f"**Selected Item: {confirmed_item['ItemName']}**")
        img_path = os.path.join(IMAGE_FOLDER, confirmed_item['ImageFile'])
        if os.path.exists(img_path):
            st.image(img_path, width=250)
        else:
            st.error(f"Image not found: {confirmed_item['ImageFile']}")

    # -----------------------------
    # Inventory Option with Session State
    # -----------------------------
    if "show_inventory" not in st.session_state:
        st.session_state.show_inventory = False

    if st.button("View Full  Inventory"):
        st.session_state.show_inventory = True

    if st.session_state.show_inventory:
        st.markdown("###  Inventory (Paginated)")
        ITEMS_PER_PAGE = 10
        total_items = len(df)
        total_pages = (total_items // ITEMS_PER_PAGE) + (1 if total_items % ITEMS_PER_PAGE != 0 else 0)

        # Use session state to store current page
        if "inventory_page" not in st.session_state:
            st.session_state.inventory_page = 1

        st.session_state.inventory_page = st.number_input(
            "Page",
            min_value=1,
            max_value=total_pages,
            value=st.session_state.inventory_page,
            step=1
        )

        start_idx = (st.session_state.inventory_page - 1) * ITEMS_PER_PAGE
        end_idx = start_idx + ITEMS_PER_PAGE
        page_items = df.iloc[start_idx:end_idx]

        for _, row in page_items.iterrows():
            st.markdown(f"**{row['ItemName']}**")
            img_path = os.path.join(IMAGE_FOLDER, row['ImageFile'])
            if os.path.exists(img_path):
                st.image(img_path, width=150)
            else:
                st.error(f"Image not found: {row['ImageFile']}")