import os
import streamlit as st
import pandas as pd
import difflib
from technician import TECHNICIAN_NAMES


# ==============================
# SESSION STATE
# ==============================
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "query_option" not in st.session_state:
    st.session_state.query_option = None


# ==============================
# HEADER
# ==============================
st.title("KDAH")
st.caption("App under development")


# ==============================
# LOGIN
# ==============================
if st.session_state.logged_in_user is None:

    name_input = st.text_input("Technician Name")

    if st.button("Login"):
        if name_input:
            cleaned = " ".join(name_input.upper().split())
            normalized = {" ".join(n.upper().split()): n for n in TECHNICIAN_NAMES}

            if cleaned in normalized:
                st.session_state.logged_in_user = normalized[cleaned]
                st.rerun()
            else:
                st.error("Enter correct name")
        else:
            st.warning("Enter name")

    st.stop()


# ==============================
# LOGOUT
# ==============================
st.success(f"Logged in as: {st.session_state.logged_in_user}")

if st.button("Logout"):
    st.session_state.logged_in_user = None
    st.session_state.query_option = None
    st.rerun()


# ==============================
# OPTION SELECT
# ==============================
if st.session_state.query_option is None:
    option = st.radio("Select Option", ["Separate Pack", "Set"])
    if st.button("Continue"):
        st.session_state.query_option = option
        st.rerun()
    st.stop()

option = st.session_state.query_option


# ==============================
# ISSUE LOG
# ==============================
LOG_FILE = "issue_log.csv"


# ==============================
# SET LOGIC (CLEAN VERSION)
# ==============================
if option == "Set":

    df = pd.read_csv("sets.csv", engine="python", on_bad_lines="skip")
    df.columns = ["SetName", "Floor"]
    df = df.apply(lambda x: x.astype(str).str.upper().str.strip())

    st.subheader("Set Query")

    name_input = st.text_input("Enter Set Name").upper().strip()

    if st.button("Search Set"):

        set_names = df["SetName"].tolist()

        # ✅ Exact Match
        if name_input in set_names:

            row = df[df["SetName"] == name_input].iloc[0]

            st.success(f"{row['SetName']} ➜ Floor: {row['Floor']}")

            if st.button("Issue Set"):

                new_entry = {
                    "Technician": st.session_state.logged_in_user,
                    "Floor": row["Floor"],
                    "ItemName": row["SetName"],
                    "Department": ""
                }

                if os.path.exists(LOG_FILE):
                    existing = pd.read_csv(LOG_FILE)
                    updated = pd.concat([existing, pd.DataFrame([new_entry])], ignore_index=True)
                else:
                    updated = pd.DataFrame([new_entry])

                updated.to_csv(LOG_FILE, index=False)

                st.success("Set Issued Successfully")

        # ✅ Suggestions Only (No Auto Floor)
        else:

            suggestions = difflib.get_close_matches(name_input, set_names, n=5, cutoff=0.3)

            if suggestions:
                st.info("Select correct name from suggestions")

                selected = st.selectbox("Suggestions", suggestions)

                if st.button("Confirm Selection"):

                    row = df[df["SetName"] == selected].iloc[0]
                    st.success(f"{row['SetName']} ➜ Floor: {row['Floor']}")

                    if st.button("Issue Selected Set"):

                        new_entry = {
                            "Technician": st.session_state.logged_in_user,
                            "Floor": row["Floor"],
                            "ItemName": row["SetName"],
                            "Department": ""
                        }

                        if os.path.exists(LOG_FILE):
                            existing = pd.read_csv(LOG_FILE)
                            updated = pd.concat([existing, pd.DataFrame([new_entry])], ignore_index=True)
                        else:
                            updated = pd.DataFrame([new_entry])

                        updated.to_csv(LOG_FILE, index=False)

                        st.success("Set Issued Successfully")

            else:
                st.error("Enter correct set name")


# ==============================
# ISSUE HISTORY
# ==============================
st.subheader("Issue History")

if os.path.exists(LOG_FILE):
    history = pd.read_csv(LOG_FILE)
    if not history.empty:
        st.dataframe(history)
    else:
        st.write("No issues recorded")
else:
    st.write("No issues recorded")