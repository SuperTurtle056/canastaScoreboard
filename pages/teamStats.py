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
df_deduct   = pd.read_sql("SELECT * FROM deductions", conn)
player_list = pd.read_sql("SELECT player FROM all_player_names", conn)["player"].tolist()

for df in [df_players, df_results, df_melds, df_deduct]:
    df["game_id"] = df["game_id"].astype(int)

st.title("Team Stats")

col1, col2 = st.columns(2)
player_1 = col1.selectbox("Player 1", player_list, index=0)
player_2 = col2.selectbox("Player 2", player_list, index=min(1, len(player_list) - 1))

if player_1 == player_2:
    st.warning("Select two different players.")
else:
    # Find completed games where both players were on the same team
    games_p1 = df_players[df_players["player"] == player_1][["game_id", "team"]].rename(columns={"team": "team_p1"})
    games_p2 = df_players[df_players["player"] == player_2][["game_id", "team"]].rename(columns={"team": "team_p2"})

    shared = games_p1.merge(games_p2, on="game_id")
    shared = shared[shared["team_p1"] == shared["team_p2"]].copy()
    shared = shared[shared["game_id"].isin(df_results["game_id"].unique())]

    if shared.empty:
        st.info(f"{player_1} and {player_2} have never played a game together.")
    else:
        game_ids  = shared["game_id"].tolist()
        team_col  = shared.set_index("game_id")["team_p1"]

        game_stats = []
        for game_id in game_ids:
            team = int(team_col[game_id])

            team_players = df_players[(df_players["game_id"] == game_id) & (df_players["team"] == team)]["player"].tolist()
            opp_players  = df_players[(df_players["game_id"] == game_id) & (df_players["team"] != team)]["player"].tolist()

            team_score = int(df_results[(df_results["game_id"] == game_id) & (df_results["player"].isin(team_players))]["score"].sum())
            opp_score  = int(df_results[(df_results["game_id"] == game_id) & (df_results["player"].isin(opp_players))]["score"].sum())

            pair_melds = df_melds[(df_melds["game_id"] == game_id) & (df_melds["player"].isin([player_1, player_2]))]
            n_melds  = len(pair_melds)
            n_jokers = int(pair_melds["jokers"].sum())
            n_twos   = int(pair_melds["twos"].sum())

            rounds_p1   = set(df_melds[(df_melds["game_id"] == game_id) & (df_melds["player"] == player_1)]["round_id"].unique())
            rounds_p2   = set(df_melds[(df_melds["game_id"] == game_id) & (df_melds["player"] == player_2)]["round_id"].unique())
            deduct_p1   = set(df_deduct[(df_deduct["game_id"] == game_id) & (df_deduct["player"] == player_1)]["round_id"].unique())
            deduct_p2   = set(df_deduct[(df_deduct["game_id"] == game_id) & (df_deduct["player"] == player_2)]["round_id"].unique())
            times_out   = len((rounds_p1 - deduct_p1) | (rounds_p2 - deduct_p2))

            game_stats.append({
                "game_id": game_id,
                "Game":        f"Game {game_id}",
                "Team Score":  team_score,
                "Opp Score":   opp_score,
                "Won":         team_score > opp_score,
                "Melds":       n_melds,
                "Jokers":      n_jokers,
                "Twos":        n_twos,
                "Went Out":    times_out,
            })

        df_stats = pd.DataFrame(game_stats)
        n_games  = len(df_stats)
        n_wins   = int(df_stats["Won"].sum())
        win_rate = n_wins / n_games

        # ── Key metrics ──────────────────────────────────────────────────────
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Games Together",      n_games)
        m2.metric("Win Rate",            f"{win_rate:.0%}")
        m3.metric("Avg Score / Game",    f"{df_stats['Team Score'].mean():.0f}")
        m4.metric("Avg Melds / Game",    f"{df_stats['Melds'].mean():.1f}")
        m5.metric("Avg Wild Cards / Game", f"{(df_stats['Jokers'] + df_stats['Twos']).mean():.1f}")

        st.markdown("---")

        chart_left, chart_right = st.columns(2)

        # ── Score per game, coloured by result ───────────────────────────────
        df_stats["Result"] = df_stats["Won"].map({True: "Win", False: "Loss"})

        fig_scores = go.Figure()
        for result, colour in [("Win", "#2ecc71"), ("Loss", "#e74c3c")]:
            mask = df_stats["Result"] == result
            fig_scores.add_trace(go.Bar(
                x=df_stats[mask]["Game"],
                y=df_stats[mask]["Team Score"],
                name=result,
                marker_color=colour,
            ))
        fig_scores.update_layout(
            title="Score per Game",
            xaxis_title=None,
            yaxis_title="Team Score",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            legend_title="Result",
        )
        chart_left.plotly_chart(fig_scores, use_container_width=True)

        # ── Individual score contribution ─────────────────────────────────────
        contrib_rows = [
            {"Game": f"Game {gid}", "Player": p,
             "Score": int(df_results[(df_results["game_id"] == gid) & (df_results["player"] == p)]["score"].sum())}
            for gid in game_ids for p in [player_1, player_2]
        ]
        df_contrib = pd.DataFrame(contrib_rows)
        fig_contrib = px.bar(
            df_contrib, x="Game", y="Score", color="Player",
            barmode="stack",
            color_discrete_sequence=["#3498db", "#9b59b6"],
            title="Score Contribution per Game",
        )
        fig_contrib.update_layout(
            xaxis_title=None,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        chart_right.plotly_chart(fig_contrib, use_container_width=True)

        st.markdown("---")

        # ── Detailed breakdown ────────────────────────────────────────────────
        left, right = st.columns(2)

        with left:
            st.subheader("Averages per Game")
            st.dataframe(pd.DataFrame({
                "Stat":    ["Melds", "Jokers", "Twos", "Rounds Went Out"],
                "Average": [
                    f"{df_stats['Melds'].mean():.1f}",
                    f"{df_stats['Jokers'].mean():.1f}",
                    f"{df_stats['Twos'].mean():.1f}",
                    f"{df_stats['Went Out'].mean():.1f}",
                ],
            }), hide_index=True, use_container_width=True)

        with right:
            st.subheader("Game Results")
            st.dataframe(
                df_stats[["Game", "Team Score", "Opp Score", "Result"]],
                hide_index=True, use_container_width=True,
            )

render_sidebar()
