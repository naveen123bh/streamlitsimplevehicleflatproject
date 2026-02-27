# plasma.py
import streamlit as st
import pandas as pd
import difflib
import os

# -----------------------------
# Load plasma CSV
# -----------------------------
pla_CSV = "plasma.csv"
IMAGE_FOLDER = "plasma_images"

df = pd.read_csv(PLA_CSV, engine="python", on_bad_lines="skip")
df.columns = ["ItemName", "ImageFile"]

# Only uppercase ItemName for search, keep ImageFile intact
df["ItemName"] = df["ItemName"].str.upper().str.strip()

st.subheader("Plasma / Instrument Section")

# -----------------------------
# Search by Name
# -----------------------------
search_input = st.text_input("Enter Item Name to Search").upper().strip()

confirmed_item = None
if search_input:
    exact = df[df["ItemName"] == search_input]
    if not exact.empty:
        confirmed_item = exact.iloc[0]
    else:
        # close match
        matches = difflib.get_close_matches(search_input, df["ItemName"].tolist(), n=5, cutoff=0.4)
        if matches:
            selected_name = st.selectbox("Did you mean:", matches)
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
# View Full Plasma Inventory (Paginated)
# -----------------------------
st.markdown("### View Full Plasma Inventory")
ITEMS_PER_PAGE = 10
total_items = len(df)
total_pages = (total_items // ITEMS_PER_PAGE) + (1 if total_items % ITEMS_PER_PAGE != 0 else 0)

page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)

start_idx = (page - 1) * ITEMS_PER_PAGE
end_idx = start_idx + ITEMS_PER_PAGE
page_items = df.iloc[start_idx:end_idx]

for _, row in page_items.iterrows():
    st.markdown(f"**{row['ItemName']}**")
    img_path = os.path.join(IMAGE_FOLDER, row['ImageFile'])
    if os.path.exists(img_path):
        st.image(img_path, width=150)
    else:
        st.error(f"Image not found: {row['ImageFile']}")