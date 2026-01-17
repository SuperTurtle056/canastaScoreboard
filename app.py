import streamlit as st
import sqlite3
from scoreCalculator import meld_score, red_threes
import pandas as pd

def get_connection():
    return sqlite3.connect("canasta.db", check_same_thread=False)

conn = get_connection()
c = conn.cursor()

# st.title("Canasta"

st.title('A Scoring and Leaderboard System for Canasta')

st.subheader('Rules')

st.markdown("""Canasta is a 4 player card game with two teams of two that uses two decks of cards with the Jokers included. The goal of the game is to reach 5000 points by creating *melds*, *canastas*, and finding red threes. 

Teams sit in an alternating arrangement; you are opposite your partner. Each player is dealt 11 cards and the rest are placed face down in the middle to create the draw pile. Any player who receives a red three in this deal must put it face up on the table and draw a new card from the draw pile. These are worth 100 points each unless a team finds all 4 red threes - they are then worth 200 points each. Any future red threes drawn are also placed face up on the table and a new card is drawn in place. If a team finds red threes but fail to make a meld then the points are deducted from the team rather than being added.
            
The top card of the draw pile is flipped over and placed next to the pile to start the discard pile. A turn follows the following order: 
1. Draw a card from the draw pile or pick up the discard pile (if able to) 
2. (Optional) Play cards - either creating melds or adding to existing ones 
3. Discard a card from hand to the discard pile""")

# Sidebar navigation
st.sidebar.page_link('app.py', label='Home')
st.sidebar.page_link('pages/leaderboard.py', label='Leaderboard')
st.sidebar.page_link('pages/playerStats.py', label='Player Stats')
st.sidebar.page_link('pages/teamStats.py', label='Team Stats')
st.sidebar.page_link('pages/startNewGame.py', label='New Game')


c.execute("""
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TEXT
)
""")
conn.commit()