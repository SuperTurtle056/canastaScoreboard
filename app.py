import streamlit as st
import sqlite3
from utils import render_sidebar

def get_connection():
    return sqlite3.connect("canasta.db", check_same_thread=False)

conn = get_connection()
c = conn.cursor()

st.title('A Scoring and Leaderboard System for Canasta')

st.subheader('Rules')

st.markdown("""Canasta is a 4 player card game with two teams of two that uses two decks of cards with the Jokers included. The goal of the game is to reach 5000 points by creating *melds*, *canastas*, and finding red threes. 

Teams sit in an alternating arrangement; you are opposite your partner. Each player is dealt 11 cards and the rest are placed face down in the middle to create the draw pile. Any player who receives a red three in this deal must put it face up on the table and draw a new card from the draw pile. These are worth 100 points each unless a team finds all 4 red threes - they are then worth 200 points each. Any future red threes drawn are also placed face up on the table and a new card is drawn in place. If a team finds red threes but fail to make a meld then the points are deducted from the team rather than being added.
            
The top card of the draw pile is flipped over and placed next to the pile to start the discard pile. A turn follows the following order: 
1. Draw a card from the draw pile or pick up the discard pile (if able to) 
2. (Optional) Play cards - either creating melds or adding to existing ones 
3. Discard a card from hand to the discard pile""")

# Sidebar navigation
render_sidebar()

if "highest_round_id" not in st.session_state:
    st.session_state['highest_round_id'] = 1 ## I don't know why this fixes everything?? Stops the session state being deleted?

c.execute("""
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TEXT,
    status TEXT
)
""")
conn.commit()


##TODO
# Logic on going out points (add new round) - have to have made a meld over 300 points.
# Logic on red threes - max number in round and double points if one team gets all
# Logic on number of cards (8 of each and 4 jokers) - some sort of error message when too many of a card are selected
# Hidden canasta button for bonus