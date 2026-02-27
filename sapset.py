import pandas as pd
import streamlit as st
import difflib
from datetime import datetime
import pytz
from streamlit_mic_recorder import mic_recorder   # ✅ added


def search_and_issue_sets(log_df, LOG_FILE, logged_user):
    """
    Handles Set Query, Department-wise viewing, and Issue logic for Streamlit app.
    Mimics separate_pack_section logic with close matches and dropdown selection.
    """

    # Load sets CSV
    df = pd.read_csv("sets.csv", engine="python", on_bad_lines="skip")
    df.columns = ["SetName", "Department", "Floor"]
    df = df.apply(lambda x: x.astype(str).str.upper().str.strip())

    st.subheader("Set Section")

    # ------------------------------
    # Safe Session Init
    # ------------------------------
    if "confirmed_set" not in st.session_state:
        st.session_state.confirmed_set = None

    if "similar_set_matches" not in st.session_state:
        st.session_state.similar_set_matches = None

    # ======================================================
    # 🟣 Search by Department
    # ======================================================
    st.markdown("### Search by Department")

    dept_input = st.text_input("Enter Department Name")

    # 🎤 Voice for Department
    st.write("🎤 Speak Department Name")
    voice_dept = mic_recorder(
        start_prompt="Start Recording",
        stop_prompt="Stop Recording",
        key="dept_mic"
    )

    if voice_dept and voice_dept["text"]:
        dept_input = voice_dept["text"]
        st.text_input("Enter Department Name", value=dept_input, key="dept_voice_fill")

    dept_input = dept_input.upper().strip()

    if dept_input:
        dept_result = df[
            df["Department"].str.contains(dept_input, case=False, na=False)
        ]

        if not dept_result.empty:
            st.write("Available Sets in Department:")
            st.dataframe(dept_result[["SetName", "Floor"]])
        else:
            st.warning("No sets found for this department")

    st.markdown("---")

    # ======================================================
    # Search by Set Name
    # ======================================================
    st.markdown("### Search by Set Name")

    name_input = st.text_input("Enter Set Name")

    # 🎤 Voice for Set Name
    st.write("🎤 Speak Set Name")
    voice_set = mic_recorder(
        start_prompt="Start Recording",
        stop_prompt="Stop Recording",
        key="set_mic"
    )

    if voice_set and voice_set["text"]:
        name_input = voice_set["text"]
        st.text_input("Enter Set Name", value=name_input, key="set_voice_fill")

    name_input = name_input.upper().strip()

    if st.button("Search Set"):

        st.session_state.confirmed_set = None
        st.session_state.similar_set_matches = None

        # exact match first
        exact = df[df["SetName"] == name_input]

        if not exact.empty:
            st.session_state.confirmed_set = exact.iloc[0].to_dict()

        else:
            # close matches
            all_names = df["SetName"].tolist()
            matches = difflib.get_close_matches(
                name_input,
                all_names,
                n=5,
                cutoff=0.4
            )

            if matches:
                st.session_state.similar_set_matches = matches
            else:
                st.error("No similar set found")

    # ------------------------------
    # Similar dropdown
    # ------------------------------
    if st.session_state.similar_set_matches:

        selected = st.selectbox(
            "Select Correct Set",
            st.session_state.similar_set_matches,
            key="selected_set_option"
        )

        if st.button("Confirm Set"):

            row = df[df["SetName"] == st.session_state.selected_set_option].iloc[0]
            st.session_state.confirmed_set = row.to_dict()
            st.session_state.similar_set_matches = None

    # ------------------------------
    # Show Confirmed Set & Issue
    # ------------------------------
    if st.session_state.confirmed_set:

        data = st.session_state.confirmed_set

        st.success(
            f"{data['SetName']} ➜ Department: {data['Department']} | Floor: {data['Floor']}"
        )

        if st.button("Issue Set"):

            ist = pytz.timezone("Asia/Kolkata")
            current_time = datetime.now(ist).strftime("%d-%m-%Y %H:%M:%S")

            new_entry = {
                "DateTime": current_time,
                "Technician": logged_user,
                "Floor": data["Floor"],
                "ItemName": data["SetName"],
                "Department": data["Department"]
            }

            log_df = pd.concat([log_df, pd.DataFrame([new_entry])], ignore_index=True)
            log_df.to_csv(LOG_FILE, index=False)

            st.success("Set Issued Successfully")

            st.session_state.confirmed_set = None

    return log_df