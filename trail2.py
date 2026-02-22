import os
import streamlit as st
import pandas as pd
import difflib
from technician import TECHNICIAN_NAMES

# ==============================
# KDHA HEADER & NOTE
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
    st.markdown(
        """
        <div style="border:3px solid blue; padding:20px; border-radius:15px; background-color:#f0f8ff; max-width:500px;">
            <h3 style='color:blue;'>CSSD Technician Login</h3>
            <p>Enter your name below:</p>
        </div>
        """, unsafe_allow_html=True
    )

    name_input = st.text_input("Technician Name", key="login_name_input")

    if name_input:
        cleaned_input = " ".join(name_input.upper().split())
        normalized_names = { " ".join(name.upper().split()): name for name in TECHNICIAN_NAMES }

        if cleaned_input in normalized_names:
            st.session_state.login_selected_name = normalized_names[cleaned_input]
        else:
            suggestions = difflib.get_close_matches(cleaned_input, normalized_names.keys(), n=5, cutoff=0.5)
            if suggestions:
                options = [normalized_names[s] for s in suggestions]
                st.session_state.login_selected_name = st.selectbox("Did you mean:", options, key="login_suggest_select")

    if st.button("Login"):
        if st.session_state.login_selected_name:
            st.session_state.logged_in_user = st.session_state.login_selected_name
        else:
            st.warning("Please enter full name or select from suggestions.")
    st.stop()

# ==============================
# LOGOUT
# ==============================
st.success(f"Logged in as: {st.session_state.logged_in_user}")
if st.button("Logout"):
    for key in ["logged_in_user","login_selected_name","current_floor","current_set","query_option"]:
        st.session_state[key] = None
    st.experimental_rerun()
    st.stop()

# ==============================
# WELCOME / QUERY CHOICE PAGE
# ==============================
if st.session_state.query_option is None:
    st.markdown("<h3 style='color:green;'>I will help you issuing Separate pack and Set to right dept/floor</h3>", unsafe_allow_html=True)
    choice = st.radio("Choose what you want to query:", ["Separate Pack", "Set"])
    if st.button("Continue"):
        st.session_state.query_option = choice
        st.experimental_rerun()
    st.stop()

option = st.session_state.query_option

# ==============================
# LOAD CSV FILES
# ==============================
# Sets
if not os.path.exists("sets.csv"):
    st.error("sets.csv file not found.")
    st.stop()
df = pd.read_csv("sets.csv", engine="python", on_bad_lines="skip")
df = df.iloc[:, :2]
df.columns = ["SetName", "Floor"]
df["SetName"] = df["SetName"].astype(str).str.upper().str.strip()
df["Floor"] = df["Floor"].astype(str).str.upper().str.strip()
set_floor_pairs = dict(zip(df["SetName"], df["Floor"]))

# Separate Packs
if option == "Separate Pack":
    if not os.path.exists("saperate_pack.csv"):
        st.error("saperate_pack.csv file not found.")
        st.stop()
    sp_df = pd.read_csv("saperate_pack.csv", engine="python", on_bad_lines="skip")
    sp_df = sp_df.iloc[:, :3]
    sp_df.columns = ["PackName", "Department", "Floor"]
    sp_df["PackName"] = sp_df["PackName"].astype(str).str.upper().str.strip()
    sp_df["Department"] = sp_df["Department"].astype(str).str.upper().str.strip()
    sp_df["Floor"] = sp_df["Floor"].astype(str).str.upper().str.strip()
    pack_floor_dept_pairs = dict(zip(sp_df["PackName"], zip(sp_df["Floor"], sp_df["Department"])))

# ==============================
# ISSUE LOG
# ==============================
LOG_FILE = "issue_log.csv"
if os.path.exists(LOG_FILE):
    log_df = pd.read_csv(LOG_FILE)
else:
    log_df = pd.DataFrame(columns=["Technician", "Floor", "SetName", "Department"])

for col in ["Technician","Floor","SetName","Department"]:
    if col not in log_df.columns:
        log_df[col] = ""
log_df = log_df[["Technician","Floor","SetName","Department"]]

# ==============================
# SEPARATE PACK PAGE
# ==============================
if option == "Separate Pack":
    sp_choice = st.radio("Choose how to view:", ["View all packs by Department & Floor", "Search by Pack Name"], index=0)

    if sp_choice == "View all packs by Department & Floor":
        dept_filter = st.selectbox("Select Department", sorted(sp_df["Department"].unique()))
        floor_filter = st.selectbox("Select Floor", sorted(sp_df["Floor"].unique()))
        filtered = sp_df[(sp_df["Department"] == dept_filter) & (sp_df["Floor"] == floor_filter)]
        if not filtered.empty:
            st.table(filtered[["PackName", "Department", "Floor"]])
        else:
            st.warning("No packs found for this Department and Floor.")

        if st.button("Issue All Filtered Packs"):
            for _, row in filtered.iterrows():
                new_entry = {
                    "Technician": st.session_state.logged_in_user,
                    "Floor": row["Floor"],
                    "SetName": row["PackName"],
                    "Department": row["Department"]
                }
                log_df = pd.concat([log_df, pd.DataFrame([new_entry])], ignore_index=True)
            log_df.to_csv(LOG_FILE, index=False)
            st.success(f"Issued {len(filtered)} packs successfully.")

    else:  # Search by Pack Name
        sp_input = st.text_input("Enter Separate Pack Name").upper().strip()
        search_pressed = st.button("Find Pack")
        if search_pressed and sp_input:
            if sp_input in pack_floor_dept_pairs:
                floor, dept = pack_floor_dept_pairs[sp_input]
                st.success(f"Pack '{sp_input}' ➜ Floor: {floor}, Department: {dept}")
                if st.button("Issue This Pack"):
                    new_entry = {
                        "Technician": st.session_state.logged_in_user,
                        "Floor": floor,
                        "SetName": sp_input,
                        "Department": dept
                    }
                    log_df = pd.concat([log_df, pd.DataFrame([new_entry])], ignore_index=True)
                    log_df.to_csv(LOG_FILE, index=False)
                    st.success(f"Pack '{sp_input}' issued successfully")
            else:
                suggestions = difflib.get_close_matches(sp_input, pack_floor_dept_pairs.keys(), n=5, cutoff=0.6)
                if suggestions:
                    st.warning("Did you mean:")
                    selected = st.selectbox("Select the correct pack", suggestions, key="suggested_packs")
                    if selected:
                        floor, dept = pack_floor_dept_pairs[selected]
                        st.success(f"Pack '{selected}' ➜ Floor: {floor}, Department: {dept}")
                        if st.button("Issue This Pack Corrected"):
                            new_entry = {
                                "Technician": st.session_state.logged_in_user,
                                "Floor": floor,
                                "SetName": selected,
                                "Department": dept
                            }
                            log_df = pd.concat([log_df, pd.DataFrame([new_entry])], ignore_index=True)
                            log_df.to_csv(LOG_FILE, index=False)
                            st.success(f"Pack '{selected}' issued successfully")

# ==============================
# SET PAGE (existing logic)
# ==============================
else:  # option == "Set"
    st.markdown("### Enter Set Name")
    user_input = st.text_input("Search Here", key="search_input")
    search_pressed = st.button("Find Floor")
    matched_set = None

    if search_pressed or user_input:
        search = user_input.upper().strip()
        if search in set_floor_pairs:
            st.session_state.current_set = search
            st.session_state.current_floor = set_floor_pairs[search]
            matched_set = search
        else:
            suggestions = difflib.get_close_matches(search, set_floor_pairs.keys(), n=5, cutoff=0.6)
            if suggestions:
                st.warning("Did you mean:")
                selected = st.selectbox("Select the correct set", suggestions, key="suggested_sets")
                if selected:
                    st.session_state.current_set = selected
                    st.session_state.current_floor = set_floor_pairs[selected]
                    matched_set = selected
            else:
                st.session_state.current_set = search
                st.session_state.current_floor = "please enter correct name"
                matched_set = search

    if st.session_state.current_floor:
        floor_name = st.session_state.current_floor
        set_name = st.session_state.current_set
        st.success(f"Floor ➜ {floor_name}")
        st.info(f"Set '{set_name}' goes to {floor_name}")
        if st.button("Issue"):
            new_entry = {
                "Technician": st.session_state.logged_in_user,
                "Floor": floor_name,
                "SetName": set_name,
                "Department": ""
            }
            log_df = pd.concat([log_df, pd.DataFrame([new_entry])], ignore_index=True)
            log_df.to_csv(LOG_FILE, index=False)
            st.success(f"{set_name} issued successfully")

# ==============================
# ISSUE HISTORY + CLEAR LOG
# ==============================
st.markdown("### Issue History")
col1, col2 = st.columns([3,1])

with col2:
    if st.button("Clear Log"):
        log_df = pd.DataFrame(columns=["Technician","Floor","SetName","Department"])
        log_df.to_csv(LOG_FILE,index=False)
        st.success("Issue history cleared")
        st.stop()

if not log_df.empty:
    for index,row in log_df.iterrows():
        dept_display = f" (Dept: {row['Department']})" if row['Department'] else ""
        st.write(f"{row['Floor']} issued by {row['Technician']} (Set/Pack: {row['SetName']}){dept_display}")
else:
    st.write("No issues recorded yet.")