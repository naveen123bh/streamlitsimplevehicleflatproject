# sap.py

import pandas as pd
import streamlit as st
import difflib


def separate_pack_section(log_df, LOG_FILE, logged_user):

    sp_df = pd.read_csv("saperate_pack.csv", engine="python", on_bad_lines="skip")
    sp_df.columns = ["PackName", "Department", "Floor"]
    sp_df = sp_df.apply(lambda x: x.astype(str).str.upper().str.strip())

    st.subheader("Separate Pack Section")

    option = st.radio(
        "Choose Method",
        ["Search by Department", "Search by Pack Name"]
    )

    # ==================================================
    # OPTION 1 → Department
    # ==================================================
    if option == "Search by Department":

        dept_input = st.text_input("Enter Department Name").upper().strip()

        if st.button("Show Packs"):

            result = sp_df[
                sp_df["Department"].str.contains(dept_input, case=False, na=False)
            ]

            if not result.empty:
                st.dataframe(result[["PackName", "Floor"]])
            else:
                st.error("No packs found")


    # ==================================================
    # OPTION 2 → Pack Name Flow
    # ==================================================
    else:

        name_input = st.text_input("Enter Pack Name").upper().strip()

        # --------------------------
        # STEP 1 → SEARCH
        # --------------------------
        if st.button("Search Pack"):

            st.session_state.confirm_pack = None
            st.session_state.found_pack = None

            exact = sp_df[sp_df["PackName"] == name_input]

            if not exact.empty:
                st.session_state.confirm_pack = exact.iloc[0].to_dict()

            else:
                all_names = sp_df["PackName"].tolist()
                matches = difflib.get_close_matches(
                    name_input, all_names, n=3, cutoff=0.4
                )

                if matches:
                    selected = st.selectbox("Did you mean:", matches)
                    st.session_state.temp_selection = selected
                else:
                    st.error("No similar pack found")

        # --------------------------
        # STEP 2 → CONFIRM (for similar)
        # --------------------------
        if st.session_state.get("temp_selection"):

            if st.button("Confirm Pack"):

                row = sp_df[
                    sp_df["PackName"] == st.session_state.temp_selection
                ].iloc[0]

                st.session_state.confirm_pack = row.to_dict()
                st.session_state.temp_selection = None

        # --------------------------
        # SHOW CONFIRMED PACK
        # --------------------------
        if st.session_state.get("confirm_pack"):

            data = st.session_state.confirm_pack

            st.success(
                f"{data['PackName']} ➜ Floor: {data['Floor']} | Dept: {data['Department']}"
            )

            # --------------------------
            # STEP 3 → ISSUE
            # --------------------------
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

                st.session_state.confirm_pack = None

    return log_df