import pandas as pd
import streamlit as st
from datetime import datetime
import pytz

def search_and_issue_sets(log_df, log_file, logged_in_user):
    """
    Handles Set Query, Search, and Issue logic for Streamlit app.
    Returns updated log_df.
    """

    # Load sets CSV
    df = pd.read_csv("sets.csv", engine="python", on_bad_lines="skip")
    df.columns = ["SetName", "Department", "Floor"]
    df = df.apply(lambda x: x.astype(str).str.upper().str.strip())

    st.subheader("Set Query")

    # Input
    name = st.text_input("Enter Set Name").upper().strip()

    if st.button("Search Set"):
        result = df[df["SetName"].str.contains(name, case=False, na=False)]

        if not result.empty:
            row = result.iloc[0]
            st.session_state.found_set = {
                "name": row["SetName"],
                "floor": row["Floor"],
                "department": row["Department"]
            }
        else:
            st.error("Set not found")

    if st.session_state.found_set:

        data = st.session_state.found_set
        st.success(f"{data['name']} ➜ Department: {data['department']} ➜ Floor: {data['floor']}")

        if st.button("Issue Set"):

            ist = pytz.timezone("Asia/Kolkata")
            current_time = datetime.now(ist).strftime("%d-%m-%Y %H:%M:%S")

            new_entry = {
                "DateTime": current_time,
                "Technician": logged_in_user,
                "Floor": data["floor"],
                "ItemName": data["name"],
                "Department": data["department"]
            }

            log_df = pd.concat([log_df, pd.DataFrame([new_entry])], ignore_index=True)
            log_df.to_csv(log_file, index=False)

            st.success("Set Issued Successfully")
            st.session_state.found_set = None

    return log_df