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

    # ==============================
    # OPTION 1 → Department wise
    # ==============================
    if option == "Search by Department":

        dept_input = st.text_input("Enter Department Name").upper().strip()

        if st.button("Show Packs"):

            result = sp_df[sp_df["Department"].str.contains(dept_input, case=False, na=False)]

            if not result.empty:
                st.write("Available Packs:")
                st.dataframe(result[["PackName", "Floor"]])
            else:
                st.error("No packs found for this department")

    # ==============================
    # OPTION 2 → Pack Name Search
    # ==============================
    else:

        name_input = st.text_input("Enter Pack Name").upper().strip()

        if st.button("Search Pack"):

            exact_match = sp_df[sp_df["PackName"] == name_input]

            # ✅ Exact Match
            if not exact_match.empty:

                row = exact_match.iloc[0]
                st.session_state.found_pack = {
                    "name": row["PackName"],
                    "floor": row["Floor"],
                    "dept": row["Department"]
                }

            # ❌ No exact → show 3 similar
            else:

                all_names = sp_df["PackName"].tolist()
                matches = difflib.get_close_matches(name_input, all_names, n=3, cutoff=0.4)

                if matches:
                    selected = st.selectbox("Did you mean:", matches)
                    if st.button("Confirm Selection"):

                        row = sp_df[sp_df["PackName"] == selected].iloc[0]

                        st.session_state.found_pack = {
                            "name": row["PackName"],
                            "floor": row["Floor"],
                            "dept": row["Department"]
                        }
                else:
                    st.error("No similar pack found")

        # ==============================
        # ISSUE LOGIC
        # ==============================
        if st.session_state.get("found_pack"):

            data = st.session_state.found_pack

            st.success(
                f"{data['name']} ➜ Floor: {data['floor']} | Dept: {data['dept']}"
            )

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