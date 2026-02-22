# sap.py

import pandas as pd
import streamlit as st

def separate_pack_section(log_df, LOG_FILE, logged_user):

    sp_df = pd.read_csv("saperate_pack.csv", engine="python", on_bad_lines="skip")
    sp_df.columns = ["PackName","Department","Floor"]
    sp_df = sp_df.apply(lambda x: x.astype(str).str.upper().str.strip())

    st.subheader("Separate Pack Query")

    name = st.text_input("Enter Pack Name").upper().strip()

    if st.button("Search Pack"):

        result = sp_df[sp_df["PackName"].str.contains(name, case=False, na=False)]

        if not result.empty:
            row = result.iloc[0]

            st.session_state.found_pack = {
                "name": row["PackName"],
                "floor": row["Floor"],
                "dept": row["Department"]
            }
        else:
            st.error("Pack not found")

    if st.session_state.found_pack:

        data = st.session_state.found_pack
        st.success(f"{data['name']} ➜ Floor: {data['floor']} | Dept: {data['dept']}")

        if st.button("Issue Pack"):

            new = {
                "Technician": logged_user,
                "Floor": data["floor"],
                "ItemName": data["name"],
                "Department": data["dept"]
            }

            log_df = pd.concat([log_df, pd.DataFrame([new])], ignore_index=True)
            log_df.to_csv(LOG_FILE, index=False)

            st.success("Pack Issued Successfully")

            st.session_state.found_pack = None