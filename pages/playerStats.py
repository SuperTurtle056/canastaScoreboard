import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import render_sidebar

def get_connection():
    return sqlite3.connect("canasta.db", check_same_thread=False)

conn = get_connection()

df_players  = pd.read_sql("SELECT game_id, team, player FROM players", conn)
df_results  = pd.read_sql("SELECT * FROM game_results", conn)
df_melds    = pd.read_sql("SELECT * FROM melds", conn)
df_red_three= pd.read_sql("SELECT * FROM red_threes", conn)
df_deduct   = pd.read_sql("SELECT * FROM deductions", conn)
df_games    = pd.read_sql("SELECT id AS game_id, start_time FROM games", conn)

for df in [df_players, df_results, df_melds, df_red_three, df_deduct, df_games]:
    df["game_id"] = df["game_id"].astype(int)

df_games["start_time"] = pd.to_datetime(df_games["start_time"])

CARD_ORDER = ["Black 3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

player_list = pd.read_sql("SELECT player FROM all_player_names", conn)["player"].tolist()

if "selected_player" not in st.session_state or st.session_state["selected_player"] not in player_list:
    st.session_state["selected_player"] = player_list[0]

player = st.selectbox("Player", player_list, key="selected_player")

player_games = df_results[df_results["player"] == player]["game_id"].tolist()

if not player_games:
    st.info(f"{player} has not completed any games yet.")
    render_sidebar()
    st.stop()

st.title(f"{player}")

# ── Determine wins per game ──────────────────────────────────────────────────
player_team = df_players[df_players["player"] == player][["game_id", "team"]]
df_with_team = df_results.merge(df_players, on=["game_id", "player"])
team_scores = df_with_team.groupby(["game_id", "team"])["score"].sum().reset_index()
winning_teams = (
    team_scores.sort_values("score", ascending=False)
    .groupby("game_id").first().reset_index()[["game_id", "team"]]
    .rename(columns={"team": "winning_team"})
)
player_with_result = (
    df_results[df_results["player"] == player]
    .merge(player_team, on="game_id")
    .merge(winning_teams, on="game_id")
)
player_with_result = player_with_result.merge(df_games, on="game_id").sort_values("start_time")
player_with_result["Won"] = player_with_result["team"] == player_with_result["winning_team"]
player_with_result["Result"] = player_with_result["Won"].map({True: "Win", False: "Loss"})
player_with_result["Game"] = player_with_result["start_time"].dt.strftime("%d %b %Y")

n_games   = len(player_with_result)
n_wins    = int(player_with_result["Won"].sum())
win_rate  = n_wins / n_games
avg_score = int(player_with_result["score"].mean())

# ── Key metrics ──────────────────────────────────────────────────────────────
m1, m2, m3 = st.columns(3)
m1.metric("Games Played", n_games)
m2.metric("Win Rate",     f"{win_rate:.0%}")
m3.metric("Avg Score",    avg_score)

st.markdown("---")

# ── Score per game chart ─────────────────────────────────────────────────────
best_idx = player_with_result["score"].idxmax()

# Work out which games are part of a streak (2+ consecutive same result)
results_list = player_with_result["Won"].tolist()
streak_colour = ["lightgray"] * len(results_list)
i = 0
while i < len(results_list):
    j = i
    while j < len(results_list) and results_list[j] == results_list[i]:
        j += 1
    if j - i >= 3:
        col = "#2ecc71" if results_list[i] else "#e74c3c"
        for k in range(i, j):
            streak_colour[k] = col
    i = j

games  = player_with_result["Game"].tolist()
scores = player_with_result["score"].tolist()

fig_score = go.Figure()

# Draw each connecting segment individually, coloured by streak membership
for idx in range(len(games) - 1):
    c1, c2 = streak_colour[idx], streak_colour[idx + 1]
    seg_col = c1 if c1 == c2 and c1 != "lightgray" else "lightgray"
    fig_score.add_trace(go.Scatter(
        x=[games[idx], games[idx + 1]],
        y=[scores[idx], scores[idx + 1]],
        mode="lines",
        line=dict(color=seg_col, width=2),
        showlegend=False, hoverinfo="skip",
    ))

# Win/loss markers (excluding best game so the star takes priority)
for result, colour in [("Win", "#2ecc71"), ("Loss", "#e74c3c")]:
    mask = (player_with_result["Result"] == result) & (player_with_result.index != best_idx)
    fig_score.add_trace(go.Scatter(
        x=player_with_result[mask]["Game"],
        y=player_with_result[mask]["score"],
        mode="markers", name=result,
        marker=dict(color=colour, size=12),
    ))

# Best game as a star, coloured by its result
best_row    = player_with_result.loc[best_idx]
star_colour = "#2ecc71" if best_row["Won"] else "#e74c3c"
fig_score.add_trace(go.Scatter(
    x=[best_row["Game"]], y=[best_row["score"]],
    mode="markers", name="Best Game",
    marker=dict(color=star_colour, size=18, symbol="star"),
))

fig_score.update_layout(
    title="Score per Game",
    xaxis_title=None,
    yaxis_title="Score",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    legend_title=None,
)
st.plotly_chart(fig_score, use_container_width=True)

st.markdown("---")

# ── Meld stats ───────────────────────────────────────────────────────────────
player_melds = df_melds[df_melds["player"] == player].copy()
player_melds["total_cards"] = player_melds["base_count"] + player_melds["twos"] + player_melds["jokers"]

melds_per_game  = player_melds.groupby("game_id").size().mean()
avg_meld_size   = player_melds["total_cards"].mean()
player_melds["is_canasta"] = player_melds["total_cards"] >= 7
canastas_per_game = player_melds.groupby("game_id")["is_canasta"].sum().mean()

# Wild cards per game
wild_per_game = player_melds.groupby("game_id").apply(
    lambda x: x["twos"].sum() + x["jokers"].sum()
).mean()

# Avg points deducted per game (completed games only)
player_deduct = df_deduct[(df_deduct["player"] == player) & (df_deduct["game_id"].isin(player_games))]
deduct_per_game = player_deduct.groupby("game_id")["points_lost"].sum().reindex(player_games, fill_value=0).mean()

# Red threes per game
rt_per_game = (
    df_red_three[df_red_three["player"] == player]
    .groupby("game_id")["card_count"].sum().mean()
)
rt_per_game = rt_per_game if not pd.isna(rt_per_game) else 0.0

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Meld Stats")
    st.metric("Avg Melds / Game",     f"{melds_per_game:.1f}")
    st.metric("Avg Meld Size",        f"{avg_meld_size:.1f} cards")
    st.metric("Avg Canastas / Game",  f"{canastas_per_game:.1f}")

with col_right:
    st.subheader("Other Stats")
    st.metric("Avg Wild Cards / Game", f"{wild_per_game:.1f}")
    st.metric("Avg Red Threes / Game", f"{rt_per_game:.1f}")
    st.metric("Avg Points Deducted / Game", f"{deduct_per_game:.0f}")

st.markdown("---")

# ── Favourite card breakdown ─────────────────────────────────────────────────
st.subheader("Cards Played")
card_stats = pd.DataFrame({
    "Card": CARD_ORDER,
    "Times Melded": [int((player_melds["base_card"] == c).sum()) for c in CARD_ORDER],
    "Avg Cards in Meld": [
        round(player_melds[player_melds["base_card"] == c]["total_cards"].mean(), 1)
        if (player_melds["base_card"] == c).any() else 0
        for c in CARD_ORDER
    ],
})
fig_cards = px.bar(
    card_stats, x="Card", y="Times Melded",
    color="Avg Cards in Meld",
    color_continuous_scale="Blues",
    range_color=[3, card_stats["Avg Cards in Meld"].max()],
    title="Melds by Card Type",
    category_orders={"Card": CARD_ORDER},
    hover_data={"Avg Cards in Meld": True},
)
fig_cards.update_layout(
    xaxis_title=None,
    xaxis_type="category",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    coloraxis_colorbar=dict(title="Avg Cards"),
)
st.plotly_chart(fig_cards, use_container_width=True)

st.markdown("---")

# ── Best teammate ────────────────────────────────────────────────────────────
st.subheader("Performance by Teammate")

teammate_rows = []
for game_id in player_games:
    p_team = df_players[(df_players["game_id"] == game_id) & (df_players["player"] == player)]["team"].values
    if not len(p_team):
        continue
    p_team = p_team[0]
    teammates = df_players[
        (df_players["game_id"] == game_id) &
        (df_players["team"] == p_team) &
        (df_players["player"] != player)
    ]["player"].tolist()
    won = bool(player_with_result.loc[player_with_result["game_id"] == game_id, "Won"].values[0]) if game_id in player_with_result["game_id"].values else False
    for t in teammates:
        teammate_rows.append({"Teammate": t, "Won": won})

if teammate_rows:
    df_teammates = pd.DataFrame(teammate_rows)
    teammate_summary = df_teammates.groupby("Teammate").agg(
        Games=("Won", "count"),
        Wins=("Won", "sum"),
    ).reset_index()
    teammate_summary["Win Rate"] = (teammate_summary["Wins"] / teammate_summary["Games"]).round(2)
    teammate_summary = teammate_summary.sort_values("Win Rate", ascending=False).reset_index(drop=True)
    st.dataframe(teammate_summary[["Teammate", "Games", "Win Rate"]], hide_index=True, use_container_width=True)

render_sidebar()
