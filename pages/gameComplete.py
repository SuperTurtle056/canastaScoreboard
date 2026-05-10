import streamlit as st
import sqlite3
import pandas as pd

## Database stuff
def get_connection():
    return sqlite3.connect("canasta.db", check_same_thread=False)

conn = get_connection()
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS awards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER UNIQUE,
    the_emperor TEXT,
    the_high_priestess TEXT,
    the_magician TEXT,
    the_chariot TEXT,
    the_hermit TEXT,
    the_hierophant TEXT,
    the_fool TEXT
)
""")
conn.commit()

game_id = st.session_state["current_game_id"]
players = pd.read_sql('SELECT * FROM players WHERE game_id = ?', conn, params = (game_id,))
players = players['player']
num_rounds = range(1,int(st.session_state["highest_round_id"])+1)

df_melds = pd.read_sql("SELECT * FROM melds WHERE game_id = ?", conn, params = (game_id,))
df_red_threes = pd.read_sql("SELECT player, round_id, card_count FROM red_threes WHERE game_id = ?", conn, params = (game_id,))
df_deductions = pd.read_sql("SELECT * FROM deductions WHERE game_id = ?", conn, params = (game_id,))
df_totals = pd.read_sql("SELECT player, score FROM game_results WHERE game_id = ?", conn, params = (game_id,))

team_1_score = df_totals.loc[(df_totals['player'] == players[0]) | (df_totals['player'] == players[1]), 'score'].sum()
team_2_score = df_totals.loc[(df_totals['player'] == players[2]) | (df_totals['player'] == players[3]), 'score'].sum()

df_totals_sorted = df_totals.sort_values(by=['score'], ascending=False) ## MVP
df_total_red_threes = (df_red_threes.groupby("player", as_index=False)["card_count"].sum()).sort_values(by=["card_count"],ascending = False)
df_total_deductions = (df_deductions.groupby("player", as_index=False)["points_lost"].sum()).sort_values(by=["points_lost"],ascending = True)

times_went_out = {player: 0 for player in players}
wild_cards_played = {player: 0 for player in players}
jokers_played = {player: 0 for player in players}
twos_played = {player: 0 for player in players}

## Create a nested dictionary of points per round
points_per_round = {player : {round_num: 0 for round_num in num_rounds} for player in players}

for player in players:
    for round in num_rounds:
        player_melds = df_melds.loc[(df_melds['player'] == player) & (df_melds['round_id'] == round)]
        player_red_threes = df_red_threes.loc[(df_red_threes['player'] == player) & (df_red_threes['round_id'] == round), 'card_count'].sum()
        player_deductions = df_deductions.loc[(df_deductions['player'] == player) & (df_deductions['round_id'] == round), 'points_lost'].sum()
        
        ## wild cards collected
        
        twos = player_melds['twos'].sum()
        jokers = player_melds['jokers'].sum()
        
        twos_played[player] += twos
        jokers_played[player] += jokers
        wild_cards_played[player] += twos + jokers
        
        ## points per round
        if player_melds['score'].sum() > 0:
            player_round_score = player_melds['score'].sum() + player_red_threes*100 - player_deductions
        else:
            player_round_score = player_melds['score'].sum() - player_red_threes*100 - player_deductions
            
        if player_deductions == 0:
            times_went_out[player] += 1
        
        points_per_round[player][round] = player_round_score

## Find highest round score and who did it
highest_score_player = None
highest_score = float("-inf")
for player, rounds in points_per_round.items():
    for round_id, score in rounds.items():
        score = int(score)
        if score > highest_score:
            highest_score = score
            highest_score_player = player

## Find who went out most often
player_went_out, player_went_out_times = max(times_went_out.items(), key=lambda x: x[1])
player_wild_cards, player_wild_cards_times = max(wild_cards_played.items(), key=lambda x: x[1])
player_jokers, player_jokers_times = max(jokers_played.items(), key=lambda x: x[1])

if team_1_score > team_2_score:
    st.title(f'Game Won by {players[0]} and {players[1]}!')
else:
    st.title(f'Game Won by {players[2]} and {players[3]}!')


## Frontend stuff
st.header('AWARDS')

col1,col2 = st.columns([0.6,0.4])

with col1:
    st.subheader(':streamlit: The Emperor', help = 'Player with the most points')
    st.subheader(':zap: The High Priestess', help = 'Player with the highest scoring round')
    st.subheader('🪄 The Magician', help = 'Player who had the most red threes')
    st.subheader(":rocket: The Chariot", help = 'Player who went out most often')
    st.subheader(":shell: The Hermit", help = 'Player with least deductions')
    st.subheader(':crystal_ball: The Hierophant', help = 'Player who played the most wild cards')
    st.subheader("🎭 The Fool", help= 'Player who played the most jokers')

with col2:
    st.subheader(f"{df_totals_sorted.iloc[0]['player']} - {df_totals_sorted.iloc[0]['score']}")
    st.subheader(f"{highest_score_player} - {highest_score}")
    
    st.subheader(f"{df_total_red_threes.iloc[0]['player']} - {df_total_red_threes.iloc[0]['card_count']}", help = f"{df_total_red_threes.iloc[1]['player']} - {df_total_red_threes.iloc[1]['card_count']}\n{df_total_red_threes.iloc[2]['player']} - {df_total_red_threes.iloc[2]['card_count']}\n{df_total_red_threes.iloc[3]['player']} - {df_total_red_threes.iloc[3]['card_count']}")
    
    st.subheader(f"{player_went_out} - {player_went_out_times}")
    st.subheader(f"{df_total_deductions.iloc[0]['player']} - {df_total_deductions.iloc[0]['points_lost']}")
    st.subheader(f"{player_wild_cards} - {player_wild_cards_times}")
    st.subheader(f"{player_jokers} - {player_jokers_times}")

## Save awards
c.execute("""INSERT OR IGNORE INTO awards (game_id, the_emperor, the_high_priestess, the_magician, the_chariot, the_hermit, the_hierophant, the_fool) VALUES (?,?,?,?,?,?,?,?) """, (game_id, df_totals_sorted.iloc[0]['player'], highest_score_player, df_total_red_threes.iloc[0]['player'], player_went_out, df_total_deductions.iloc[0]['player'],player_wild_cards,player_jokers))

conn.commit()


newcol1, newcol2 = st.columns([0.6,0.4])

with newcol1:
    if st.button('Review Scorecard'):
        st.switch_page('pages/currentGame.py')
    
with newcol2:
    if st.button('Home'):
        st.switch_page('app.py')