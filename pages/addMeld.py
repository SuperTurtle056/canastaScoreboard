import streamlit as st
import sqlite3
from scoreCalculator import meld_score, red_threes
import pandas as pd

game_id = st.session_state["current_game_id"]
selected_round_id = int(st.session_state["selected_round_id"])
player = st.session_state["selected_player"]


def reset_meld_inputs():
    st.session_state.base_count = 2
    st.session_state.twos_count = 0
    st.session_state.jokers_count = 0
    
def save_and_reset(game_id, round_id, player, base_card, base_count, twos, jokers,score):
    c.execute("""
                INSERT INTO melds 
                (game_id, round_id, player, base_card, base_count, twos, jokers, score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (game_id, round_id, player, base_card, base_count, twos, jokers, score))
    
    reset_meld_inputs()

    conn.commit()
    st.success(f"Saved {score} points for {player} in round {round_id}")
    

def get_connection():
    return sqlite3.connect("canasta.db", check_same_thread=False)

conn = get_connection()
c = conn.cursor()

st.title("Meld Input")

base_card = st.selectbox("Card", ['Black 3',"4","5","6","7","8","9","10","J","Q","K","A"], key = 'base_card')

if base_card == 'Black 3':
    base_count = st.number_input("How many?", 2, 4, key = 'base_count')
else:
    base_count = st.number_input("How many?", 2, 8, key = 'base_count')
    
twos = st.number_input("Number of Twos", 0,8, key = 'twos_count')
jokers = st.number_input('Number of Jokers',0,4, key = 'jokers_count')

col1, col2 = st.columns([0.7,0.3])

with col1:
    if base_count + twos + jokers >= 3:
        score = meld_score(base_card, base_count, twos, jokers)
        st.write("Score for this meld:", score)
        
        newcol1, newcol2 = st.columns(2)
        
        with newcol1:
            if st.button("Save meld"):
                c.execute("""
                INSERT INTO melds 
                (game_id, round_id, player, base_card, base_count, twos, jokers, score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (game_id, selected_round_id, player, base_card, base_count, twos, jokers, score))

                conn.commit()
                st.success(f"Saved {score} points for {player} in round {selected_round_id}")
                
                st.switch_page('pages/currentGame.py')
                st.rerun()
        
        with newcol2:
            st.button("Add Another", on_click=save_and_reset, args =(game_id,selected_round_id,player,base_card,base_count,twos,jokers,score))
                

    else:
        st.write("Add more cards for a meld!")

with col2:
    if st.button('Cancel'):
        st.switch_page('pages/currentGame.py')

