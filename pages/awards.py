import streamlit as st
import sqlite3
from scoreCalculator import meld_score, red_threes
import pandas as pd

def get_connection():
    return sqlite3.connect("canasta.db", check_same_thread=False)

conn = get_connection()
c = conn.cursor()

player_df = pd.read_sql('SELECT player FROM all_player_names', conn)

st.title("Awards")

if st.button(" ", key="emperor", help="The Emperor"):
    st.session_state["flipped_emperor"] = True

st.image("images/the_emperor.jpg")



st.sidebar.page_link('app.py', label='Home')
st.sidebar.page_link('pages/leaderboard.py', label='Leaderboard')
st.sidebar.page_link('pages/awards.py', label='Awards')
st.sidebar.page_link('pages/teamStats.py', label='Team Stats')
st.sidebar.page_link('pages/continueGame.py', label='Continue Game')
st.sidebar.page_link('pages/startNewGame.py', label='New Game')