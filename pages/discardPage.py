import streamlit as st
import sqlite3
from scoreCalculator import meld_score, red_threes
import pandas as pd
import numpy as np

game_id = st.session_state["current_game_id"]

## Database stuff
def get_connection():
    return sqlite3.connect("canasta.db", check_same_thread=False)

conn = get_connection()
c = conn.cursor()

st.title('Are You Sure?')

col1, col2 = st.columns([0.7,0.3])

with col1:
    if st.button('Yes'):
        c.execute("""DELETE FROM deductions WHERE game_id = ?""", (game_id,))
        c.execute("""DELETE FROM melds WHERE game_id = ?""", (game_id,))
        c.execute("""DELETE FROM players WHERE game_id = ?""", (game_id,))
        c.execute("""DELETE FROM red_threes WHERE game_id = ?""", (game_id,))
        c.execute("""DELETE FROM games WHERE id = ?""", (game_id,))

        conn.commit()
        st.switch_page('app.py')
        
with col2:
    if st.button('No'):
        st.switch_page('pages/currentGame.py')