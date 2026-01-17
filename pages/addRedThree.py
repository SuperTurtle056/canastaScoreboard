import streamlit as st
import sqlite3
from scoreCalculator import meld_score, red_threes
import pandas as pd

game_id = st.session_state["current_game_id"]

def get_connection():
    return sqlite3.connect("canasta.db", check_same_thread=False)

conn = get_connection()
c = conn.cursor()

players = pd.read_sql('SELECT * FROM players WHERE game_id = ?', conn, params = (game_id,))
players = players['player']

st.title("Red Three Input")

first_col1, first_col2 = st.columns(2)

with first_col1:
    player = st.selectbox("Player", players)
    st.markdown('###')
    
with first_col2:
    round_id = st.number_input("Round Number", min_value=1, step=1)
    st.markdown('###')

card_count = st.number_input("How many?", 1, 4)

col1, col2 = st.columns(2)
with col1:
    if st.button("Save"):
        c.execute("""
        INSERT INTO red_threes 
        (game_id, round_id, player, card_count)
        VALUES (?, ?, ?, ?)
    """, (game_id, round_id, player, card_count))

        conn.commit()
        if card_count > 1:
            st.success(f"Saved {card_count} Red Threes for {player} in round {round_id}")
        else:
            st.success(f"Saved {card_count} Red Three for {player} in round {round_id}")
        
        st.switch_page('pages/currentGame.py')

with col2:
    if st.button('Cancel'):
        st.switch_page('pages/currentGame.py')


# # Sidebar navigation
# st.sidebar.page_link('app.py', label='Home')
# st.sidebar.page_link('pages/currentGame.py', label='Current Game')