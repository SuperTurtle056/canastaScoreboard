import streamlit as st
import sqlite3
from scoreCalculator import meld_score, red_threes
import pandas as pd

def get_connection():
    return sqlite3.connect("canasta.db", check_same_thread=False)

conn = get_connection()
c = conn.cursor()

st.title('Continue Game')

# games_playing_df = pd.read_sql('SELECT * FROM games WHERE status = ?', conn, params = ('playing',))
games_playing_df = pd.read_sql('SELECT * FROM games', conn)

for game_id in games_playing_df['id']:
    date_started = games_playing_df.loc[games_playing_df["id"] == game_id, "start_time"].iloc[0]
    date_started = pd.to_datetime(date_started).strftime("%d %b %Y, %H:%M")
    if st.button(f"Continue Game Sarted On: {date_started}"):
        st.session_state["current_game_id"] = game_id

        round_df = pd.read_sql(
            "SELECT round_id FROM melds WHERE game_id = ?",
            conn,
            params=(game_id,)
        )

        if round_df.empty:
            st.session_state["highest_round_id"] = 1
        else:
            st.session_state["highest_round_id"] = int(round_df["round_id"].max())

        st.switch_page("pages/currentGame.py")

st.sidebar.page_link('app.py', label='Home')
st.sidebar.page_link('pages/leaderboard.py', label='Leaderboard')
st.sidebar.page_link('pages/playerStats.py', label='Player Stats')
st.sidebar.page_link('pages/teamStats.py', label='Team Stats')
st.sidebar.page_link('pages/continueGame.py', label='Continue Game')
st.sidebar.page_link('pages/startNewGame.py', label='New Game')