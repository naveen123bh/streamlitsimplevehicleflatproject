# sap.py

import pandas as pd
import streamlit as st
import difflib


def separate_pack_section(log_df, LOG_FILE, logged_user):

    sp_df = pd.read_csv("saperate_pack.csv", engine="python", on_bad_lines="skip")
    sp_df.columns = ["PackName", "Department", "Floor"]
    sp_df = sp_df.apply(lambda x: x.astype(str).str.upper().str.strip())

    st.subheader("Separate Pack Section")

    # initialize state safely
    if "confirmed_pack" not in st.session_state:
        st.session_state.confirmed_pack = None

    name_input = st.text_input("Enter Pack Name").upper().strip()

    # ===============================
    # SEARCH
    # ===============================
    if st.button("Search Pack"):

        st.session_state.confirmed_pack = None

        exact = sp_df[sp_df["PackName"] == name_input]

        if not exact.empty:

            st.session_state.confirmed_pack = exact.iloc[0].to_dict()

        else:

            all_names = sp_df["PackName"].tolist()
            matches = difflib.get_close_matches(
                name_input, all_names, n=3, cutoff=0.4
            )

            if matches:
                selected = st.selectbox("Select Correct Pack", matches)
                st.session_state.selected_option = selected
            else:
                st.error("No similar pack found")

    # ===============================
    # CONFIRM SIMILAR
    # ===============================
    if "selected_option" in st.session_state:

        if st.button("Confirm Pack"):

            row = sp_df[
                sp_df["PackName"] == st.session_state.selected_option
            ].iloc[0]

            st.session_state.confirmed_pack = row.to_dict()
            del st.session_state.selected_option

    # ===============================
    # SHOW CONFIRMED PACK
    # ===============================
    if st.session_state.confirmed_pack:

        data = st.session_state.confirmed_pack

        st.success(
            f"{data['PackName']} ➜ Floor: {data['Floor']} | Dept: {data['Department']}"
        )

        # ===============================
        # ISSUE (Only Confirmed One)
        # ===============================
        if st.button("Issue Pack"):

            new = {
                "Technician": logged_user,
                "Floor": data["Floor"],
                "ItemName": data["PackName"],
                "Department": data["Department"]
            }

            log_df = pd.concat(
                [log_df, pd.DataFrame([new])],
                ignore_index=True
            )

            log_df.to_csv(LOG_FILE, index=False)

            st.success("Pack Issued Successfully")

            # clear after issuing
            st.session_state.confirmed_pack = None

    return log_df