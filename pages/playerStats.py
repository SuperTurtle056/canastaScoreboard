import streamlit as st
import sqlite3
from scoreCalculator import meld_score, red_threes
import pandas as pd

def get_connection():
    return sqlite3.connect("canasta.db", check_same_thread=False)

conn = get_connection()
c = conn.cursor()

player_df = pd.read_sql('SELECT player FROM all_player_names', conn)

st.title("Player Stats")

st.selectbox('Select Player', player_df['player'])

#TODO

# Graph of points per game, wins/losses are different colours - win rate on graph
# Favourite card to meld
# Number of games played
# Number of wild cards played
# Best teammate

st.sidebar.page_link('app.py', label='Home')
st.sidebar.page_link('pages/leaderboard.py', label='Leaderboard')
st.sidebar.page_link('pages/playerStats.py', label='Player Stats')
st.sidebar.page_link('pages/teamStats.py', label='Team Stats')
st.sidebar.page_link('pages/continueGame.py', label='Continue Game')
st.sidebar.page_link('pages/startNewGame.py', label='New Game')