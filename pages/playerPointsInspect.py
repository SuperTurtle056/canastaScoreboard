import streamlit as st
import sqlite3
import pandas as pd

def get_connection():
    return sqlite3.connect("canasta.db", check_same_thread=False)

conn = get_connection()
c = conn.cursor()

game_id = st.session_state["current_game_id"]
selected_round_id = int(st.session_state["selected_round_id"])
player = st.session_state["selected_player"]

st.title(f'{player} Points in Round {selected_round_id}')

df_melds = pd.read_sql("SELECT base_card, base_count, twos, jokers, score FROM melds WHERE game_id = ? AND round_id = ? AND player = ?", conn, params = (game_id, selected_round_id, player))

df_red_threes = pd.read_sql("SELECT card_count FROM red_threes WHERE game_id = ? AND round_id = ? AND player = ?", conn, params = (game_id, selected_round_id, player))

df_deductions = pd.read_sql("SELECT points_lost FROM deductions WHERE game_id = ? AND round_id = ? AND player = ?", conn, params = (game_id, selected_round_id, player))


col1, col2, col3 = st.columns([0.2,0.6,0.2])

with col1:
    st.write('Red Threes')
    st.write(df_red_threes['card_count'].sum())
    
with col2:
    st.write('Melds')
    st.write(df_melds)
    subcol1, subcol2, subcol3, subcol4, subcol5 = st.columns(5)

with col3:
    st.write('Deductions')
    st.write(df_deductions['points_lost'].sum())


newcol1, newcol2, newcol3 = st.columns([0.4,0.4,0.2])
with newcol1:    
    if st.button('Red Three',icon="➕"):
        c.execute("""
        INSERT INTO red_threes 
        (game_id, round_id, player, card_count)
        VALUES (?, ?, ?, ?)
    """, (game_id, selected_round_id, player, 1))

        conn.commit()
        st.rerun()
    
with newcol2:
    if st.button('Meld', icon="➕"):
        st.switch_page('pages/addMeld.py')
with newcol3:
    if st.button('Deductions', icon="➕"):
        st.switch_page('pages/handDeductions.py')


with newcol2:
    if st.button('Back'):
        st.switch_page('pages/currentGame.py')