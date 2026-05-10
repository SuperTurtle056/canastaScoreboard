import streamlit as st
import sqlite3
from utils import render_sidebar
import pandas as pd

def get_connection():
    return sqlite3.connect("canasta.db", check_same_thread=False)

conn = get_connection()
c = conn.cursor()

player_df = pd.read_sql('SELECT player FROM all_player_names', conn)


st.title("Leaderboard")

st.write(player_df)

##TODO
# show: win rate, average points per game, average wild cards played per game
# order by choice


render_sidebar()