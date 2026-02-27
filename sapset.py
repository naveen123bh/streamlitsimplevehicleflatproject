import pandas as pd
import streamlit as st
import difflib
from datetime import datetime
import pytz
import streamlit.components.v1 as components


def search_and_issue_sets(log_df, LOG_FILE, logged_user):

    df = pd.read_csv("sets.csv", engine="python", on_bad_lines="skip")
    df.columns = ["SetName", "Department", "Floor"]
    df = df.apply(lambda x: x.astype(str).str.upper().str.strip())

    st.subheader("Set Section")

    if "confirmed_set" not in st.session_state:
        st.session_state.confirmed_set = None

    # ======================================================
    # Search by Department
    # ======================================================
    st.markdown("### Search by Department")

    dept_input = st.text_input("Enter Department Name").upper().strip()

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
    # Live Search by Set Name (Voice Enabled)
    # ======================================================
    st.markdown("### Search by Set Name")

    name_input = st.text_input("Enter Set Name", key="set_text").upper().strip()

    # 🎤 Voice Button
    components.html("""
    <script>
    function startDictation() {
        if ('webkitSpeechRecognition' in window) {

            var recognition = new webkitSpeechRecognition();
            recognition.lang = "en-US";
            recognition.start();

            recognition.onresult = function(event) {
                const text = event.results[0][0].transcript.toUpperCase();

                const inputs = window.parent.document.querySelectorAll('input');

                inputs.forEach(input => {
                    if (input.placeholder === "Enter Set Name") {
                        input.value = text;
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                });
            };

        } else {
            alert("Speech Recognition not supported in this browser.");
        }
    }
    </script>

    <button onclick="startDictation()" 
    style="padding:8px 16px;font-size:16px;cursor:pointer;">
    🎤 Speak
    </button>
    """, height=80)

    # ================= LIVE FILTER =================
    if name_input:

        filtered = df[df["SetName"].str.contains(name_input, case=False, na=False)]

        if not filtered.empty:

            selected_set = st.selectbox(
                "Select Set",
                filtered["SetName"].unique(),
                key="live_select"
            )

            row = df[df["SetName"] == selected_set].iloc[0]
            st.session_state.confirmed_set = row.to_dict()

        else:
            st.warning("No matching set found")
            st.session_state.confirmed_set = None

    else:
        st.session_state.confirmed_set = None

    # ======================================================
    # Confirmed Set & Issue
    # ======================================================
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