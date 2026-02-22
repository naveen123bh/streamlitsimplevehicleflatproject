import os
import streamlit as st
import pandas as pd
import difflib
from technician import TECHNICIAN_NAMES

# ==============================
# HEADER
# ==============================
st.markdown("<h2 style='color:purple; font-weight:bold;'>KDAH</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:orange; font-style:italic;'>Note: This app is under development and consideration</p>", unsafe_allow_html=True)

# ==============================
# SESSION STATE
# ==============================
for key in ["logged_in_user","current_floor","current_set","login_selected_name","query_option"]:
    if key not in st.session_state:
        st.session_state[key] = None

# ==============================
# LOGIN PAGE
# ==============================
if st.session_state.logged_in_user is None:

    st.markdown("""
    <div style="border:3px solid blue; padding:20px; border-radius:15px; background-color:#f0f8ff; max-width:500px;">
        <h3 style='color:blue;'>CSSD Technician Login</h3>
        <p>Enter your name below:</p>
    </div>
    """, unsafe_allow_html=True)

    name_input = st.text_input("Technician Name")

    if name_input:
        cleaned = " ".join(name_input.upper().split())
        normalized = { " ".join(name.upper().split()): name for name in TECHNICIAN_NAMES }

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
            st.warning("Enter full correct name.")

    st.stop()

# ==============================
# LOGOUT
# ==============================
st.success(f"Logged in as: {st.session_state.logged_in_user}")

if st.button("Logout"):
    for key in st.session_state.keys():
        st.session_state[key] = None
    st.rerun()

# ==============================
# WELCOME PAGE
# ==============================
if st.session_state.query_option is None:

    st.markdown("<h3 style='color:green;'>I will help you issuing Separate pack and Set to right dept/floor</h3>", unsafe_allow_html=True)

    choice = st.radio("Choose what you want to query:", ["Separate Pack", "Set"])

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
    log_df = pd.read_csv(LOG_FILE)
else:
    log_df = pd.DataFrame(columns=["Technician","Floor","ItemName","Department"])

# ==============================
# SEPARATE PACK PAGE
# ==============================
if option == "Separate Pack":

    if not os.path.exists("saperate_pack.csv"):
        st.error("saperate_pack.csv not found")
        st.stop()

    sp_df = pd.read_csv("saperate_pack.csv")
    sp_df.columns = ["PackName","Department","Floor"]
    sp_df = sp_df.apply(lambda x: x.astype(str).str.upper().str.strip())

    pack_dict = dict(zip(sp_df["PackName"], zip(sp_df["Floor"], sp_df["Department"])))

    st.subheader("Separate Pack Query")

    mode = st.radio("Select Option", ["View by Department & Floor","Search by Pack Name"])

    if mode == "View by Department & Floor":
        dept = st.selectbox("Department", sorted(sp_df["Department"].unique()))
        floor = st.selectbox("Floor", sorted(sp_df["Floor"].unique()))

        filtered = sp_df[(sp_df["Department"]==dept) & (sp_df["Floor"]==floor)]

        if not filtered.empty:
            st.table(filtered)

            if st.button("Issue All"):
                for _, row in filtered.iterrows():
                    new = {
                        "Technician": st.session_state.logged_in_user,
                        "Floor": row["Floor"],
                        "ItemName": row["PackName"],
                        "Department": row["Department"]
                    }
                    log_df = pd.concat([log_df, pd.DataFrame([new])], ignore_index=True)
                log_df.to_csv(LOG_FILE,index=False)
                st.success("Issued successfully")
        else:
            st.warning("No pack found")

    else:
        name = st.text_input("Enter Pack Name").upper().strip()

        if st.button("Search"):
            if name in pack_dict:
                floor, dept = pack_dict[name]
                st.success(f"{name} ➜ Floor: {floor}, Department: {dept}")

                if st.button("Issue This Pack"):
                    new = {
                        "Technician": st.session_state.logged_in_user,
                        "Floor": floor,
                        "ItemName": name,
                        "Department": dept
                    }
                    log_df = pd.concat([log_df, pd.DataFrame([new])], ignore_index=True)
                    log_df.to_csv(LOG_FILE,index=False)
                    st.success("Issued successfully")
            else:
                st.error("Pack not found")

# ==============================
# SET PAGE
# ==============================
else:

    if not os.path.exists("sets.csv"):
        st.error("sets.csv not found")
        st.stop()

    df = pd.read_csv("sets.csv")
    df.columns = ["SetName","Floor"]
    df = df.apply(lambda x: x.astype(str).str.upper().str.strip())

    set_dict = dict(zip(df["SetName"], df["Floor"]))

    st.subheader("Set Query")

    name = st.text_input("Enter Set Name").upper().strip()

    if st.button("Search Set"):
        if name in set_dict:
            floor = set_dict[name]
            st.success(f"{name} ➜ Floor: {floor}")

            if st.button("Issue This Set"):
                new = {
                    "Technician": st.session_state.logged_in_user,
                    "Floor": floor,
                    "ItemName": name,
                    "Department": ""
                }
                log_df = pd.concat([log_df, pd.DataFrame([new])], ignore_index=True)
                log_df.to_csv(LOG_FILE,index=False)
                st.success("Issued successfully")
        else:
            st.error("Set not found")

# ==============================
# ISSUE HISTORY
# ==============================
st.subheader("Issue History")

if not log_df.empty:
    st.table(log_df)
else:
    st.write("No issues recorded")