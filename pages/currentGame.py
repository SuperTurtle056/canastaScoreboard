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

st.markdown(
    """
    <style>
    div.stButton > button > div {
        font-family: "Courier New", sans-serif !important;
        font-size: 14px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


game_id = st.session_state["current_game_id"]

def new_round():
    st.session_state["highest_round_id"] +=1

df_melds = pd.read_sql("SELECT * FROM melds WHERE game_id = ?", conn, params = (game_id,))
df_red_threes = pd.read_sql("SELECT * FROM red_threes WHERE game_id = ?", conn, params = (game_id,))
df_deductions = pd.read_sql("SELECT * FROM deductions WHERE game_id = ?", conn, params = (game_id,))


num_rounds = range(1,int(st.session_state["highest_round_id"])+1)

players = pd.read_sql('SELECT * FROM players WHERE game_id = ?', conn, params = (game_id,))
players = players['player']

st.title("Scorecard")

col1, col2, col3 = st.columns([0.15,0.425,0.425], vertical_alignment='bottom')

## Just for the looks
with col1:
    for round in num_rounds:
        st.button(f'Round {round}:', key = f'round_{round}')
    st.button('Total:', key = 'total')

## Shows team 1 info
with col2:
    df_meld_player_1 = df_melds[df_melds['player'] == players[0]]
    df_red_threes_player_1 = pd.read_sql('SELECT * FROM red_threes WHERE player = ? AND game_id = ?', conn, params=(players[0], game_id,))
    df_deductions_player_1 = pd.read_sql('SELECT * FROM deductions WHERE player = ? AND game_id = ?', conn, params=(players[0], game_id,))
    df_meld_player_2 = df_melds[df_melds['player'] == players[1]]
    df_red_threes_player_2 = pd.read_sql('SELECT * FROM red_threes WHERE player = ? AND game_id = ?', conn, params=(players[1], game_id,))
    df_deductions_player_2 = pd.read_sql('SELECT * FROM deductions WHERE player = ? AND game_id = ?', conn, params=(players[1], game_id,))
    
    st.subheader('Team 1')  
    col2_1, col2_2,col2_3 = st.columns([0.35,0.35,0.3])
    with col2_1:
        st.write(players[0])
    with col2_2:
        st.write(players[1])
    with col2_3:
        st.write('Total')
    
    player_1_scores = []
    player_2_scores = []
    
    for round in num_rounds:
        st.session_state["selected_round_id"] = round
        
        with col2_1:
            score_player_1 = df_meld_player_1.loc[df_meld_player_1['round_id'] == round, 'score'].sum() + red_threes(df_red_threes_player_1.loc[df_red_threes_player_1['round_id'] == round, 'card_count'].sum()) - df_deductions_player_1.loc[df_deductions_player_1['round_id'] == round, 'points_lost'].sum()
            
            if df_deductions_player_1.loc[df_deductions_player_1['round_id'] == round, 'points_lost'].sum() == 0:
                score_player_1 += 100
                if st.button(f':violet[{score_player_1}]', key = f'p1_inspect_{round}'):
                    st.session_state["selected_player"] = players[0]
                    st.switch_page("pages/playerPointsInspect.py")
            else:
                if st.button(f'{score_player_1}', key = f'p1_inspect_{round}'):
                    st.session_state["selected_player"] = players[0]
                    st.switch_page("pages/playerPointsInspect.py")
                    
            player_1_scores.append(score_player_1)
            
        with col2_2:
            score_player_2 = df_meld_player_2.loc[df_meld_player_2['round_id'] == round, 'score'].sum() + red_threes(df_red_threes_player_2.loc[df_red_threes_player_2['round_id'] == round, 'card_count'].sum()) - df_deductions_player_2.loc[df_deductions_player_2['round_id'] == round, 'points_lost'].sum()
            
            if df_deductions_player_2.loc[df_deductions_player_2['round_id'] == round, 'points_lost'].sum() == 0:
                score_player_2 += 100
                if st.button(f':violet[{score_player_2}]', key = f'p2_inspect_{round}'):
                    st.session_state["selected_player"] = players[1]
                    st.switch_page("pages/playerPointsInspect.py")
                
            else:
                if st.button(f'{score_player_2}', key = f'p2_inspect_{round}'):
                    st.session_state["selected_player"] = players[1]
                    st.switch_page("pages/playerPointsInspect.py")
            player_2_scores.append(score_player_2)
            
        with col2_3:
            st.button(f'{score_player_1+score_player_2}', key = f'team_1_total_{round}')
    
    with col2_1:
        st.button(f'{sum(player_1_scores)}', key = 'p1_total')
    with col2_2:
        st.button(f'{sum(player_2_scores)}', key = 'p2_total')
    with col2_3:
        team_1_total = sum(player_1_scores) + sum(player_2_scores)
        if team_1_total < 1500:
            st.button(f':green[{team_1_total}]', key = 'team_1_total')
        elif team_1_total < 3000:
            st.button(f':orange[{team_1_total}]', key = 'team_1_total')
        else:
            st.button(f':red[{team_1_total}]', key = 'team_1_total')
    
## Shows team 2 info    
with col3:
    df_meld_player_3 = df_melds[df_melds['player'] == players[2]]
    df_red_threes_player_3 = pd.read_sql('SELECT * FROM red_threes WHERE player = ? AND game_id = ?', conn, params=(players[2], game_id,))
    df_deductions_player_3 = pd.read_sql('SELECT * FROM deductions WHERE player = ? AND game_id = ?', conn, params=(players[2], game_id,))
    df_meld_player_4 = df_melds[df_melds['player'] == players[3]]
    df_red_threes_player_4 = pd.read_sql('SELECT * FROM red_threes WHERE player = ? AND game_id = ?', conn, params=(players[3], game_id,))
    df_deductions_player_4 = pd.read_sql('SELECT * FROM deductions WHERE player = ? AND game_id = ?', conn, params=(players[3], game_id,))
    
    st.subheader('Team 2')
    
    col3_1, col3_2,col3_3 = st.columns([0.35,0.35,0.3])
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
                if st.button(f':violet[{score_player_3}]', key = f'p3_inspect_{round}'):
                    st.session_state["selected_player"] = players[2]
                    st.switch_page("pages/playerPointsInspect.py")
            else:
                if st.button(f'{score_player_3}', key = f'p3_inspect_{round}'):
                    st.session_state["selected_player"] = players[2]
                    st.switch_page("pages/playerPointsInspect.py")
                    
            player_3_scores.append(score_player_3)
            
        with col3_2:
            score_player_4 = df_meld_player_4.loc[df_meld_player_4['round_id'] == round, 'score'].sum() + red_threes(df_red_threes_player_4.loc[df_red_threes_player_4['round_id'] == round, 'card_count'].sum()) - df_deductions_player_4.loc[df_deductions_player_4['round_id'] == round, 'points_lost'].sum()
            if df_deductions_player_4.loc[df_deductions_player_4['round_id'] == round, 'points_lost'].sum() == 0:
                score_player_4 += 100
                if st.button(f':violet[{score_player_4}]', key = f'p4_inspect_{round}'):
                    st.session_state["selected_player"] = players[3]
                    st.switch_page("pages/playerPointsInspect.py")
            else:
                if st.button(f'{score_player_4}', key = f'p4_inspect_{round}'):
                    st.session_state["selected_player"] = players[3]
                    st.switch_page("pages/playerPointsInspect.py")
            player_4_scores.append(score_player_4)
        with col3_3:
            st.button(f'{score_player_3+score_player_4}', key = f'team_2_total_{round}')
    
    with col3_1:
        st.button(f'{sum(player_3_scores)}', key = 'p3_total')
    with col3_2:
        st.button(f'{sum(player_4_scores)}', key = 'p4_total')
    with col3_3:
        team_2_total = sum(player_3_scores) + sum(player_4_scores)
        if team_2_total < 1500:
            st.button(f':green[{team_2_total}]', key = 'team_2_total')
        elif team_2_total < 3000:
            st.button(f':orange[{team_2_total}]', key = 'team_2_total')
        else:
            st.button(f':red[{team_2_total}]', key = 'team_2_total')


newcols1, newcols2, newcols3 = st.columns([0.35,0.4,0.22])

with newcols2:
    st.button('New Round', on_click=new_round, icon = '➕')
        
## End game buttons
newnewcols1, newnewcols2, newnewcols3, newnewcols4, newnewcols5 = st.columns([0.3,0.05,0.3,0.05,0.3])
with newnewcols1:
    if st.button('Save'):
        if sum(player_3_scores) + sum(player_4_scores) > 5000 or sum(player_1_scores) + sum(player_2_scores) > 5000:
            st.switch_page('app.py')
        else:
            st.toast('No Winner Yet!')
            
with newnewcols3:
    if st.button('Continue Later'):
        st.switch_page('app.py')

with newnewcols5:
    if st.button('Discard'):
        st.switch_page('pages/discardPage.py')
        
st.sidebar.page_link('app.py', label='Home')
st.sidebar.page_link('pages/leaderboard.py', label='Leaderboard')
st.sidebar.page_link('pages/playerStats.py', label='Player Stats')
st.sidebar.page_link('pages/teamStats.py', label='Team Stats')
st.sidebar.page_link('pages/continueGame.py', label='Continue Game')
st.sidebar.page_link('pages/startNewGame.py', label='New Game')