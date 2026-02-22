import os
import streamlit as st
import pandas as pd
import difflib
from technician import TECHNICIAN_NAMES
from sap import separate_pack_section
from datetime import datetime
import pytz


# ==============================
# SESSION STATE INIT
# ==============================
defaults = {
    "logged_in_user": None,
    "login_selected_name": None,
    "query_option": None,
    "found_pack": None,
    "found_set": None
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ==============================
# HEADER
# ==============================
st.markdown("<h2 style='color:purple;'>KDAH</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:orange;'>Note: App under development</p>", unsafe_allow_html=True)


# ==============================
# LOGIN
# ==============================
if st.session_state.logged_in_user is None:

    name_input = st.text_input("Technician Name")

    if name_input:
        cleaned = " ".join(name_input.upper().split())
        normalized = {" ".join(n.upper().split()): n for n in TECHNICIAN_NAMES}

        if cleaned in normalized:
            st.session_state.login_selected_name = normalized[cleaned]
        else:
            suggestions = difflib.get_close_matches(cleaned, normalized.keys(), n=5, cutoff=0.5)
            if suggestions:
                options = [normalized[s] for s in suggestions]
                st.session_state.login_selected_name = st.selectbox("Did you mean:", options)

    if st.button("Login"):
        if st.session_state.login_selected_name:
            st.session_state.logged_in_user = st.session_state.login_selected_name
            st.rerun()
        else:
            st.warning("Enter correct name")

    st.stop()


# ==============================
# LOGOUT
# ==============================
st.success(f"Logged in as: {st.session_state.logged_in_user}")

if st.button("Logout"):
    for key in defaults.keys():
        st.session_state[key] = None
    st.rerun()


# ==============================
# OPTION SELECT
# ==============================
if st.session_state.query_option is None:

    choice = st.radio("Select Option", ["Separate Pack", "Set"])

    if st.button("Continue"):
        st.session_state.query_option = choice
        st.rerun()

    st.stop()

option = st.session_state.query_option


# ==============================
# ISSUE LOG
# ==============================
LOG_FILE = "issue_log.csv"

if os.path.exists(LOG_FILE):
    log_df = pd.read_csv(LOG_FILE, engine="python", on_bad_lines="skip")
else:
    log_df = pd.DataFrame(
        columns=["DateTime", "Technician", "Floor", "ItemName", "Department"]
    )


# ==============================
# SEPARATE PACK
# ==============================
if option == "Separate Pack":
    log_df = separate_pack_section(
        log_df,
        LOG_FILE,
        st.session_state.logged_in_user
    )


# ==============================
# SET SECTION
# ==============================
else:

    df = pd.read_csv("sets.csv", engine="python", on_bad_lines="skip")
    df.columns = ["SetName", "Floor"]
    df = df.apply(lambda x: x.astype(str).str.upper().str.strip())

    st.subheader("Set Query")

    name = st.text_input("Enter Set Name").upper().strip()

    if st.button("Search Set"):

        result = df[df["SetName"].str.contains(name, case=False, na=False)]

        if not result.empty:
            row = result.iloc[0]
            st.session_state.found_set = {
                "name": row["SetName"],
                "floor": row["Floor"]
            }
        else:
            st.error("Set not found")

    if st.session_state.found_set:

        data = st.session_state.found_set
        st.success(f"{data['name']} ➜ Floor: {data['floor']}")

        if st.button("Issue Set"):

            ist = pytz.timezone("Asia/Kolkata")
            current_time = datetime.now(ist).strftime("%d-%m-%Y %H:%M:%S")

            new = {
                "DateTime": current_time,
                "Technician": st.session_state.logged_in_user,
                "Floor": data["floor"],
                "ItemName": data["name"],
                "Department": ""
            }

            log_df = pd.concat([log_df, pd.DataFrame([new])], ignore_index=True)
            log_df.to_csv(LOG_FILE, index=False)

            st.success("Set Issued Successfully")
            st.session_state.found_set = None


# ==============================
# ISSUE HISTORY
# ==============================
st.subheader("Issue History")

if not log_df.empty:
    st.dataframe(log_df)
else:
    st.write("No issues recorded")

if st.button("Clear Log History"):

    empty_df = pd.DataFrame(
        columns=["DateTime", "Technician", "Floor", "ItemName", "Department"]
    )

    empty_df.to_csv(LOG_FILE, index=False)

    st.success("Log Cleared Successfully")
    st.rerun()