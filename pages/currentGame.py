import streamlit as st
import sqlite3
from scoreCalculator import meld_score, red_threes
import pandas as pd
import numpy as np

## Database stuff
def get_connection():
    return sqlite3.connect("canasta.db", check_same_thread=False)

conn = get_connection()
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS melds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id TEXT,
    round_id INTEGER,
    player TEXT,
    base_card TEXT,
    base_count INTEGER,
    twos INTEGER,
    jokers INTEGER,
    score INTEGER
)
""")
conn.commit()

c.execute("""
CREATE TABLE IF NOT EXISTS red_threes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id TEXT,
    round_id INTEGER,
    player TEXT,
    card_count INTEGER
)
""")
conn.commit()

c.execute("""
CREATE TABLE IF NOT EXISTS deductions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id TEXT,
    round_id INTEGER,
    player TEXT,
    points_lost INTEGER
)
""")
conn.commit()

game_id = st.session_state["current_game_id"]
df_melds = pd.read_sql("SELECT * FROM melds WHERE game_id = ?", conn, params = (game_id,))
df_red_threes = pd.read_sql("SELECT * FROM red_threes WHERE game_id = ?", conn, params = (game_id,))
df_deductions = pd.read_sql("SELECT * FROM deductions WHERE game_id = ?", conn, params = (game_id,))

## Convoluted way of checking each df to see which has the most rounds stored (otherwise inputting red threes without others doesnt update scores)
unique_rounds = [df_melds['round_id'].unique(),df_red_threes['round_id'].unique(),df_deductions['round_id'].unique()]
length_rounds = [len(x) for x in unique_rounds]
longest_index = np.argmax(np.array(length_rounds))
num_rounds = unique_rounds[longest_index]

players = pd.read_sql('SELECT * FROM players WHERE game_id = ?', conn, params = (game_id,))
players = players['player']

st.title("Scorecard")
col1, col2, col3 = st.columns([0.1,0.45,0.45], vertical_alignment='bottom')

## Just for the looks
with col1:
    for round in num_rounds:
        st.write(f'Round {round}:')
    st.write('Total:')

## Shows team 1 info
with col2:
    df_meld_player_1 = df_melds[df_melds['player'] == players[0]]
    df_red_threes_player_1 = pd.read_sql('SELECT * FROM red_threes WHERE player = ? AND game_id = ?', conn, params=(players[0], game_id,))
    df_deductions_player_1 = pd.read_sql('SELECT * FROM deductions WHERE player = ? AND game_id = ?', conn, params=(players[0], game_id,))
    df_meld_player_2 = df_melds[df_melds['player'] == players[1]]
    df_red_threes_player_2 = pd.read_sql('SELECT * FROM red_threes WHERE player = ? AND game_id = ?', conn, params=(players[1], game_id,))
    df_deductions_player_2 = pd.read_sql('SELECT * FROM deductions WHERE player = ? AND game_id = ?', conn, params=(players[1], game_id,))
    
    st.subheader('Team 1')  
    col2_1, col2_2,col2_3 = st.columns([0.4,0.4,0.2])
    with col2_1:
        st.write(players[0])
    with col2_2:
        st.write(players[1])
    with col2_3:
        st.write('Total')
    
    player_1_scores = []
    player_2_scores = []
    
    for round in num_rounds:
        with col2_1:
            score_player_1 = df_meld_player_1.loc[df_meld_player_1['round_id'] == round, 'score'].sum() + red_threes(df_red_threes_player_1.loc[df_red_threes_player_1['round_id'] == round, 'card_count'].sum()) - df_deductions_player_1.loc[df_deductions_player_1['round_id'] == round, 'points_lost'].sum()
            if df_deductions_player_1.loc[df_deductions_player_1['round_id'] == round, 'points_lost'].sum() == 0:
                score_player_1 += 100
                st.write(score_player_1,"(O)")
            else:
                st.write(score_player_1)
            player_1_scores.append(score_player_1)
        with col2_2:
            score_player_2 = df_meld_player_2.loc[df_meld_player_2['round_id'] == round, 'score'].sum() + red_threes(df_red_threes_player_2.loc[df_red_threes_player_2['round_id'] == round, 'card_count'].sum()) - df_deductions_player_2.loc[df_deductions_player_2['round_id'] == round, 'points_lost'].sum()
            if df_deductions_player_2.loc[df_deductions_player_2['round_id'] == round, 'points_lost'].sum() == 0:
                score_player_2 += 100
                st.write(score_player_2,"(O)")
            else:
                st.write(score_player_2)
            player_2_scores.append(score_player_2)
        with col2_3:
            st.write(score_player_1+score_player_2)
    
    with col2_1:
        st.write(sum(player_1_scores))
    with col2_2:
        st.write(sum(player_2_scores))
    with col2_3:
        st.write(sum(player_1_scores) + sum(player_2_scores))
    
## Shows team 2 info    
with col3:
    df_meld_player_3 = df_melds[df_melds['player'] == players[2]]
    df_red_threes_player_3 = pd.read_sql('SELECT * FROM red_threes WHERE player = ? AND game_id = ?', conn, params=(players[2], game_id,))
    df_deductions_player_3 = pd.read_sql('SELECT * FROM deductions WHERE player = ? AND game_id = ?', conn, params=(players[2], game_id,))
    df_meld_player_4 = df_melds[df_melds['player'] == players[3]]
    df_red_threes_player_4 = pd.read_sql('SELECT * FROM red_threes WHERE player = ? AND game_id = ?', conn, params=(players[3], game_id,))
    df_deductions_player_4 = pd.read_sql('SELECT * FROM deductions WHERE player = ? AND game_id = ?', conn, params=(players[3], game_id,))
    
    st.subheader('Team 2')
    
    col3_1, col3_2,col3_3 = st.columns([0.4,0.4,0.2])
    with col3_1:
        st.write(players[2])
    with col3_2:
        st.write(players[3])
    with col3_3:
        st.write('Total')
    
    player_3_scores = []
    player_4_scores = []
    
    for round in num_rounds:
        with col3_1:
            score_player_3 = df_meld_player_3.loc[df_meld_player_3['round_id'] == round, 'score'].sum() + red_threes(df_red_threes_player_3.loc[df_red_threes_player_3['round_id'] == round, 'card_count'].sum()) - df_deductions_player_3.loc[df_deductions_player_3['round_id'] == round, 'points_lost'].sum()
            if df_deductions_player_3.loc[df_deductions_player_3['round_id'] == round, 'points_lost'].sum() == 0:
                score_player_3 += 100
                st.write(score_player_3,"(O)")
            else:
                st.write(score_player_3)
            player_3_scores.append(score_player_3)
        with col3_2:
            score_player_4 = df_meld_player_4.loc[df_meld_player_4['round_id'] == round, 'score'].sum() + red_threes(df_red_threes_player_4.loc[df_red_threes_player_4['round_id'] == round, 'card_count'].sum()) - df_deductions_player_4.loc[df_deductions_player_4['round_id'] == round, 'points_lost'].sum()
            if df_deductions_player_4.loc[df_deductions_player_4['round_id'] == round, 'points_lost'].sum() == 0:
                score_player_4 += 100
                st.write(score_player_4,"(O)")
            else:
                st.write(score_player_4)
            player_4_scores.append(score_player_4)
        with col3_3:
            st.write(score_player_3+score_player_4)
    
    with col3_1:
        st.write(sum(player_3_scores))
    with col3_2:
        st.write(sum(player_4_scores))
    with col3_3:
        st.write(sum(player_3_scores) + sum(player_4_scores))


## Useful buttons
newcols1, newcols2, newcols3 = st.columns(3)
with newcols1:
    st.page_link("pages/addRedThree.py", label="Add Red Threes", icon="➕")
with newcols2:
    st.page_link("pages/addMeld.py", label="Add Meld", icon="➕")
with newcols3:
    st.page_link("pages/handDeductions.py", label="Left in Hand", icon="➕")


## End game buttons
newnewcols1, newnewcols2 = st.columns(2)
with newnewcols1:
    if st.button('Save'):
        if sum(player_3_scores) + sum(player_4_scores) > 5000 or sum(player_1_scores) + sum(player_2_scores):
            st.switch_page('app.py')
        else:
            st.toast('No Winner Yet!')

with newnewcols2:
    if st.button('Discard'):
        c.execute("""DELETE FROM deductions WHERE game_id = ?""", (game_id,))
        c.execute("""DELETE FROM melds WHERE game_id = ?""", (game_id,))
        c.execute("""DELETE FROM players WHERE game_id = ?""", (game_id,))
        c.execute("""DELETE FROM red_threes WHERE game_id = ?""", (game_id,))
        c.execute("""DELETE FROM games WHERE id = ?""", (game_id,))

        conn.commit()
        st.switch_page('app.py')