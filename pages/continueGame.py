import streamlit as st
import sqlite3
from scoreCalculator import meld_score, red_threes
import pandas as pd

def get_connection():
    return sqlite3.connect("canasta.db", check_same_thread=False)

conn = get_connection()
c = conn.cursor()

st.title('Continue Game')

game_id = st.number_input("Game ID", min_value=1, step=1)


if st.button("Continue"):
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