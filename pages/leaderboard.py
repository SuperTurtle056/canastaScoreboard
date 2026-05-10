import streamlit as st
import sqlite3
import pandas as pd
from utils import render_sidebar

def get_connection():
    return sqlite3.connect("canasta.db", check_same_thread=False)

conn = get_connection()

df_results = pd.read_sql("SELECT * FROM game_results", conn)
df_players = pd.read_sql("SELECT game_id, team, player FROM players", conn)
df_melds   = pd.read_sql("SELECT game_id, player, twos, jokers FROM melds", conn)
df_results["game_id"] = df_results["game_id"].astype(int)
df_players["game_id"] = df_players["game_id"].astype(int)
df_melds["game_id"]   = df_melds["game_id"].astype(int)

# Determine winner of each game by comparing team scores
df_with_team = df_results.merge(df_players, on=["game_id", "player"])
team_scores  = df_with_team.groupby(["game_id", "team"])["score"].sum().reset_index()

winning_teams = (
    team_scores.sort_values("score", ascending=False)
    .groupby("game_id")
    .first()
    .reset_index()[["game_id", "team"]]
    .rename(columns={"team": "winning_team"})
)

df_with_team = df_with_team.merge(winning_teams, on="game_id")
df_with_team["won"] = df_with_team["team"] == df_with_team["winning_team"]

# Wild cards per player per game, then average across games
df_melds["wild_cards"] = df_melds["twos"] + df_melds["jokers"]
wild_per_game = (
    df_melds.groupby(["game_id", "player"])["wild_cards"].sum()
    .reset_index()
)
avg_wild = wild_per_game.groupby("player")["wild_cards"].mean().round(1).rename("Avg Wild Cards")

# Aggregate per player
summary = df_with_team.groupby("player").agg(
    Games_Played=("game_id", "nunique"),
    Wins=("won", "sum"),
    Avg_Score=("score", "mean"),
).reset_index()

summary["Win Rate"] = (summary["Wins"] / summary["Games_Played"]).round(2)
summary["Avg Score"] = summary["Avg_Score"].round(0).astype(int)
summary = summary.merge(avg_wild, on="player", how="left")

leaderboard = (
    summary[["player", "Games_Played", "Win Rate", "Avg Score", "Avg Wild Cards"]]
    .rename(columns={"player": "Player", "Games_Played": "Games Played"})
    .sort_values("Win Rate", ascending=False)
    .reset_index(drop=True)
)

st.title("Leaderboard")
st.caption("Click a row to view that player's stats.")

sort_col = st.selectbox("Sort by", leaderboard.columns[1:], index=1)
leaderboard = leaderboard.sort_values(sort_col, ascending=False).reset_index(drop=True)

selection = st.dataframe(leaderboard, hide_index=True, use_container_width=True,
                         on_select="rerun", selection_mode="single-row")

if selection.selection.rows:
    selected_player = leaderboard.iloc[selection.selection.rows[0]]["Player"]
    st.session_state["selected_player"] = selected_player
    st.switch_page("pages/playerStats.py")

##TODO
# Players selectable to see into individual stats

render_sidebar()
