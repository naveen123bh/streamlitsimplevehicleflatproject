import streamlit as st
import os
import random
import base64

# =====================================
# PAGE CONFIG
# =====================================
st.set_page_config(page_title="Music App", layout="centered")

# =====================================
# GET RANDOM SONG FROM CURRENT DIRECTORY
# =====================================
def get_random_song():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    songs = [f for f in os.listdir(current_dir) if f.endswith(".mp3")]
    
    if songs:
        return os.path.join(current_dir, random.choice(songs))
    return None

# =====================================
# AUTOPLAY FUNCTION
# =====================================
def autoplay_audio(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()

    audio_html = f"""
    <audio autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# =====================================
# MAIN
# =====================================

song = get_random_song()

if song:
    st.write("🎵 Now Playing:")
    st.success(os.path.basename(song))
    autoplay_audio(song)
else:
    st.error("No MP3 files found in same folder as main.py")