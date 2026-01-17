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

st.title("Deductions")

CARD_SCORES= {
    'Black 3': 5,
    '4': 5,
    '5': 5,
    '6': 5,
    '7': 5,
    '8': 10,
    '9': 10,
    '10': 10,
    'Jack': 10,
    'Queen': 10,
    'King': 10,
    'Ace': 20,
    '2': 20,
    'Joker': 50
}

first_col1, first_col2 = st.columns(2)

with first_col1:
    player = st.selectbox("Player", players)
    st.markdown('###')
    
with first_col2:
    round_id = st.number_input("Round Number", min_value=1, step=1)
    st.markdown('###')


col1, col2 = st.columns(2)
total = 0
run_over = 0
for card_name, value in CARD_SCORES.items():
    
    if run_over < 7:
        with col1:
            num_cards = st.number_input(f"{card_name}",0,8, key=f'{card_name} input')
            total += num_cards*value
            run_over += 1
    else:      
        with col2:
                num_cards = st.number_input(f"{card_name}",0,8, key=f'{card_name} input')
                total += num_cards*value
                run_over += 1

newcols1, newcols2, newcols3 = st.columns(3)

with newcols1:
    if st.button('Save'):
        c.execute("""
            INSERT INTO deductions 
            (game_id, round_id, player, points_lost)
            VALUES (?, ?, ?, ?)
        """, (game_id, round_id, player, total))

        conn.commit()
        st.switch_page('pages/currentGame.py')

with newcols2:
    if st.button('Cancel'):
        st.switch_page('pages/currentGame.py')

with newcols3:
    st.write(total)