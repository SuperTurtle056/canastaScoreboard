import streamlit as st
import sqlite3
from scoreCalculator import meld_score, red_threes
import pandas as pd

def get_connection():
    return sqlite3.connect("canasta.db", check_same_thread=False)

conn = get_connection()
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS all_player_names (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player TEXT
)
""")
conn.commit()

c.execute("""
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id TEXT,
    team INTEGER,
    player TEXT
)
""")
conn.commit()

st.title("New Game")

st.subheader('Choose Teams')
col1, col2 = st.columns(2)

player_df = pd.read_sql('SELECT * FROM all_player_names', conn)
player_list = player_df['player'].unique()

with st.form("add_player_form", clear_on_submit=True):
    player_name = st.text_input("Input New Player")
    submitted = st.form_submit_button("Add Player")

    if submitted:
        if not player_name.strip():
            st.warning("Enter a name")
        elif player_name in player_list:
            st.warning("Player already exists")
        else:
            c.execute("INSERT INTO all_player_names (player) VALUES (?)", (player_name,))
            conn.commit()
            st.success(f"Added {player_name}")

player_df = pd.read_sql("SELECT * FROM all_player_names", conn)
player_list = player_df["player"].tolist()

with col1:
    st.write('Team 1')
    col1_1, col1_2 = st.columns(2)
    with col1_1:
        player_1 = st.selectbox('Player 1:',player_list)
    with col1_2:
        player_2 = st.selectbox('Player 2:',player_list)
    

with col2:
    st.write('Team 2')
    col2_1, col2_2 = st.columns(2)
    with col2_1:
        player_3 = st.selectbox('Player 3:',player_list)
    with col2_2:
        player_4 = st.selectbox('Player 4:',player_list)


if st.button('Start Game'):
    current_players = [player_1,player_2,player_3,player_4]
    
    ## Making sure there are 4 distinct players
    if len(set(current_players)) == 4:
        teams = [1,1,2,2]
        
        c.execute("INSERT INTO games (start_time, status) VALUES (datetime('now'), ?)", ('playing',))
        conn.commit()

        game_id = c.lastrowid
        st.session_state["current_game_id"] = game_id
        st.session_state["highest_round_id"] = 1
        
        for index in range(4):
            c.execute("INSERT INTO players (game_id, team, player) VALUES (?,?,?)", (game_id, teams[index], current_players[index]))
            conn.commit()
        
        st.success(f"Game {game_id} started")
        st.switch_page('pages/currentGame.py')
    
    else:
        st.warning('You have duplicate players!')
    
   
st.sidebar.page_link('app.py', label='Home')
st.sidebar.page_link('pages/leaderboard.py', label='Leaderboard')
st.sidebar.page_link('pages/playerStats.py', label='Player Stats')
st.sidebar.page_link('pages/teamStats.py', label='Team Stats')
st.sidebar.page_link('pages/continueGame.py', label='Continue Game')
st.sidebar.page_link('pages/startNewGame.py', label='New Game')