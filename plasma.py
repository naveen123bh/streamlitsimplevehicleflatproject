import os
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

def plasma_section():
    """
    Handles Plasma / Instrument Recognition section in Streamlit.
    Mimics the sapset.py structure.
    """

    df = pd.read_csv("plasma.csv", engine="python", on_bad_lines="skip")
    df["ItemName"] = df["ItemName"].str.upper().str.strip()

    st.subheader("Plasma / Instrument Section")

    # Session State
    if "plasma_search_result" not in st.session_state:
        st.session_state.plasma_search_result = None

    # ======================================================
    # Option Selection
    # ======================================================
    choice = st.radio(
        "Choose Option",
        ["Search by Name", "View Full Inventory"]
    )

    # ======================================================
    # Search by Name
    # ======================================================
    if choice == "Search by Name":
        name_input = st.text_input("Enter Item Name", key="plasma_name_text")

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
                        if (input.placeholder === "Enter Item Name") {
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

        if name_input:
            search_text = name_input.upper().strip()
            result = df[df["ItemName"].str.contains(search_text, na=False)]

            st.session_state.plasma_search_result = result

        if st.session_state.plasma_search_result is not None:
            if not st.session_state.plasma_search_result.empty:
                for _, row in st.session_state.plasma_search_result.iterrows():
                    image_path = os.path.join("plasma_images", row["ImageFile"])
                    st.image(image_path, caption=row["ItemName"], width=300)
            else:
                st.warning("No item found")

    # ======================================================
    # View Full Inventory
    # ======================================================
    if choice == "View Full Inventory":
        st.markdown("### Full Plasma Inventory")
        for _, row in df.iterrows():
            image_path = os.path.join("plasma_images", row["ImageFile"])
            st.image(image_path, caption=row["ItemName"], width=200)