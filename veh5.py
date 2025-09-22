import os
import re
import sys
import streamlit as st
import pandas as pd

# ===== Python version check =====
st.write("Python version:", sys.version)

st.title("Rishabh Tower Security", anchor=None)
st.markdown("<h1 style='color:darkblue; font-size:70px; text-align:center;'>Rishabh Tower Security</h1>", unsafe_allow_html=True)

# ===== Vehicle-Flat mapping =====
vehicle_flat_pairs = {
    "MH01CW8883": "F1402",
    "MH01AW0076": "F803",
    "MH01DV7905": "F803",
    "MH01BL4073": "F1001",
    "MH01CY4916": "F1101",
    "MH01DV4548": "F1101",
    "MH01AS7283": "F1103",
    "MH01BW8739": "F1201",
    "MH01AJ1280": "F1201",
    "MH01CW1103": "F1202",
    "MH01DN8388": "F1202",
    "MH01DS8388": "F1202",
    "MH01DF8883": "F1402",
    "MH47AG8208": "F1501",
    "MH01CS1389": "F1501",
    "MH01DF8922": "F1501",
    "MH02FT6906": "F301",
    "MH01VE9542": "F1404",
    "KL250825": "F702",
    "MH01BV4719": "F1503",
    "MH01DC4468": "F1103",
    "MH01EC4345": "F303",
    "MH01EG4466": "F1404",
    "MH01BR3809": "F1303",
    "MH01DH8262": "F1202",
    "MH01EC1731": "F103",
    "MH01EC6173": "F103",
    "MH01ED5928": "F104",
    "MH01BV9157": "F105",
    "MH01BS5970": "F406",
    "MH01BN6173": "F204",
    "MH01CZ8751": "F204",
    "MH46BC6962": "F205",
    "MH01CW8808": "F206",
    "MH01AY3291": "F306",
    "MH45P6581": "F401",
    "MHGJ10CE1771": "F403",
    "MH01Z4903": "F403",
    "MH01CW5160": "F403",
    "MH46DZ5084": "F403",
    "MH46AS5358": "F404",
    "MH01DM3960": "F405",
    "MH01CB5008": "F405",
    "MH01CZ0743": "F504",
    "MH01CX9174": "F505",
    "MH46BR6433": "F506",
    "MH46BX7368": "F506",
    "MH01RA3013": "F601",
    "MH14E7323": "F601",
    "MH14BS7612": "F605",
    "MH43BS6225": "F606",
    "JK02AJ9532": "F701",
    "MH01EG1167": "F701",
    "KL25P0885": "F702",
    "PB12N9278": "F502",
    "DL95BC4754": "F402",
    "DL95AY2413": "F501",
    "MH01ED1470": "F203",
    "MH01DD9066": "F705",
    "MH01DE8241": "F1104",
    "MH01DD0634": "F1105",
    "MHED4100": "F1203",
    "MH01AS5210": "F1203",
    "MH01CX5210": "F1204",
    "MH01DM8542": "F1304",
    "MH01BZ7329": "F1502",
    "MH47BE1895": "F305",
    "GJ10CE2279": "F602",
    "MH01BF2532": "F101",
    "AQ7283": "F1103",
    "23BH1092B": "F104",
    "CP9561": "FRELIANCE",
    "MH01DB6179": "F504",
    "MH03EH6869": "F705",
    # Add all other vehicles from your previous lists here carefully...
}

# ===== Normalize dictionary keys =====
vehicle_flat_pairs = {k.strip().upper(): v.strip().upper() for k, v in vehicle_flat_pairs.items()}

# ===== Helper functions =====
def normalize_vehicle_input(vehicle_number):
    """Normalize vehicle number: case-insensitive, remove spaces/newlines, replace O with 0."""
    if pd.isna(vehicle_number):
        return ""
    text = str(vehicle_number).upper()
    text = re.sub(r"\s+", "", text)        # remove ALL whitespace
    text = text.replace("O", "0")          # replace letter O with zero
    return text.strip()

def normalize_flat_input(flat_number):
    """Normalize flat number: case-insensitive, remove spaces/newlines."""
    if pd.isna(flat_number):
        return ""
    text = str(flat_number).upper()
    text = re.sub(r"\s+", "", text)        # remove ALL whitespace
    return text.strip()

# ===== Streamlit UI =====
st.markdown("<h2 style='color:green; font-size:50px;'>Vehicle या Flat Number डालें</h2>", unsafe_allow_html=True)
user_input = st.text_input("", placeholder="Vehicle या Flat Number डालें", key="input_box", max_chars=20, help=None)
st.markdown("<br>", unsafe_allow_html=True)

if st.button("Result Dekhe"):
    if user_input:
        input_norm_vehicle = normalize_vehicle_input(user_input)
        input_norm_flat = normalize_flat_input(user_input)

        # Check Vehicle
        if input_norm_vehicle in vehicle_flat_pairs:
            st.markdown(f"<h2 style='color:purple; font-size:50px;'>Flat number(s) for vehicle {input_norm_vehicle}: {vehicle_flat_pairs[input_norm_vehicle]}</h2>", unsafe_allow_html=True)
        # Check Flat
        elif input_norm_flat in vehicle_flat_pairs.values():
            matching_vehicles = [v for v, f in vehicle_flat_pairs.items() if f == input_norm_flat]
            st.markdown(f"<h2 style='color:purple; font-size:50px;'>Vehicle number(s) for flat {input_norm_flat}: {', '.join(matching_vehicles)}</h2>", unsafe_allow_html=True)
        else:
            st.markdown("<h2 style='color:red; font-size:50px;'>वाहन सूची अपडेट की जा रही है। कार्य प्रगति में है..<br>कृपया 2 दिन प्रतीक्षा करें: लेखक इस पर काम कर रहे हैं।</h2>", unsafe_allow_html=True)
