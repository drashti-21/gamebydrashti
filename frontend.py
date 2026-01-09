import streamlit as st
import subprocess
import sys

# Page config
st.set_page_config(page_title="Game Launcher", layout="centered")

# Center the button using columns
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🎮 Start Game", use_container_width=True):
        # Run game.py
        subprocess.Popen([sys.executable, "game.py"])
        st.success("Game started!")
