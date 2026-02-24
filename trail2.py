import streamlit as st
import os
import random
import base64
import time

# =====================================
# PAGE CONFIG
# =====================================
st.set_page_config(page_title="My Music App", layout="centered")

# =====================================
# MUSIC FOLDER (Put all mp3 inside this)
# =====================================
MUSIC_FOLDER = "songs"

# =====================================
# GET RANDOM SONG (Every Refresh New)
# =====================================
def get_random_song():
    songs = [f for f in os.listdir(MUSIC_FOLDER) if f.endswith(".mp3")]
    if songs:
        return os.path.join(MUSIC_FOLDER, random.choice(songs))
    return None

# =====================================
# AUTOPLAY AUDIO FUNCTION
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
# MAIN LOGIC
# =====================================

if os.path.exists(MUSIC_FOLDER):

    # force refresh trick (helps autoplay)
    if "refresh" not in st.session_state:
        st.session_state.refresh = time.time()

    song = get_random_song()

    if song:
        st.write("🎵 Now Playing:")
        st.success(os.path.basename(song))
        autoplay_audio(song)
    else:
        st.warning("No MP3 files found inside 'songs' folder.")

else:
    st.error("❌ 'songs' folder not found. Please create it and add mp3 files.")