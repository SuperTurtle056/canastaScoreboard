import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import render_sidebar

def get_connection():
    return sqlite3.connect("canasta.db", check_same_thread=False)

conn = get_connection()

df_players   = pd.read_sql("SELECT game_id, team, player FROM players", conn)
df_results   = pd.read_sql("SELECT * FROM game_results", conn)
df_melds     = pd.read_sql("SELECT * FROM melds", conn)
df_deduct    = pd.read_sql("SELECT * FROM deductions", conn)
df_red_three = pd.read_sql("SELECT * FROM red_threes", conn)
df_games     = pd.read_sql("SELECT id AS game_id, start_time FROM games", conn)
player_list  = pd.read_sql("SELECT player FROM all_player_names", conn)["player"].tolist()

for df in [df_players, df_results, df_melds, df_deduct, df_red_three, df_games]:
    df["game_id"] = df["game_id"].astype(int)

df_games["start_time"] = pd.to_datetime(df_games["start_time"])

CARD_ORDER = ["Black 3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

st.title("Team Stats")

col1, col2 = st.columns(2)
player_1 = col1.selectbox("Player 1", player_list, index=0)
player_2 = col2.selectbox("Player 2", player_list, index=min(1, len(player_list) - 1))

if player_1 == player_2:
    st.warning("Select two different players.")
else:
    games_p1 = df_players[df_players["player"] == player_1][["game_id", "team"]].rename(columns={"team": "team_p1"})
    games_p2 = df_players[df_players["player"] == player_2][["game_id", "team"]].rename(columns={"team": "team_p2"})
    shared   = games_p1.merge(games_p2, on="game_id")
    shared   = shared[shared["team_p1"] == shared["team_p2"]].copy()
    shared   = shared[shared["game_id"].isin(df_results["game_id"].unique())]

    if shared.empty:
        st.info(f"{player_1} and {player_2} have never played a game together.")
    else:
        game_ids = shared["game_id"].tolist()
        team_col = shared.set_index("game_id")["team_p1"]

        game_stats = []
        for game_id in game_ids:
            team         = int(team_col[game_id])
            team_players = df_players[(df_players["game_id"] == game_id) & (df_players["team"] == team)]["player"].tolist()
            opp_players  = df_players[(df_players["game_id"] == game_id) & (df_players["team"] != team)]["player"].tolist()
            team_score   = int(df_results[(df_results["game_id"] == game_id) & (df_results["player"].isin(team_players))]["score"].sum())
            opp_score    = int(df_results[(df_results["game_id"] == game_id) & (df_results["player"].isin(opp_players))]["score"].sum())
            pair_melds_g = df_melds[(df_melds["game_id"] == game_id) & (df_melds["player"].isin([player_1, player_2]))]
            game_stats.append({
                "game_id":    game_id,
                "Team Score": team_score,
                "Opp Score":  opp_score,
                "Won":        team_score > opp_score,
                "Melds":      len(pair_melds_g),
                "Jokers":     int(pair_melds_g["jokers"].sum()),
                "Twos":       int(pair_melds_g["twos"].sum()),
            })

        df_stats = (
            pd.DataFrame(game_stats)
            .merge(df_games, on="game_id")
            .sort_values("start_time")
        )
        df_stats["Result"] = df_stats["Won"].map({True: "Win", False: "Loss"})
        df_stats["Game"]   = df_stats["start_time"].dt.strftime("%d %b %Y")

        n_games  = len(df_stats)
        n_wins   = int(df_stats["Won"].sum())
        win_rate = n_wins / n_games

        # ── Combined meld data across all shared games ───────────────────────
        pair_melds = df_melds[
            df_melds["player"].isin([player_1, player_2]) &
            df_melds["game_id"].isin(game_ids)
        ].copy()
        pair_melds["total_cards"] = pair_melds["base_count"] + pair_melds["twos"] + pair_melds["jokers"]
        pair_melds["is_canasta"]  = pair_melds["total_cards"] >= 7

        avg_meld_size     = pair_melds["total_cards"].mean()
        canastas_per_game = pair_melds.groupby("game_id")["is_canasta"].sum().reindex(game_ids, fill_value=0).mean()
        wild_per_game     = (df_stats["Jokers"] + df_stats["Twos"]).mean()

        pair_rt        = df_red_three[df_red_three["player"].isin([player_1, player_2]) & df_red_three["game_id"].isin(game_ids)]
        rt_per_game    = pair_rt.groupby("game_id")["card_count"].sum().reindex(game_ids, fill_value=0).mean()

        pair_deduct      = df_deduct[df_deduct["player"].isin([player_1, player_2]) & df_deduct["game_id"].isin(game_ids)]
        deduct_per_game  = pair_deduct.groupby("game_id")["points_lost"].sum().reindex(game_ids, fill_value=0).mean()

        # ── Key metrics ──────────────────────────────────────────────────────
        m1, m2, m3 = st.columns(3)
        m1.metric("Games Together",        n_games)
        m2.metric("Win Rate",              f"{win_rate:.0%}")
        m3.metric("Avg Score / Game",      f"{df_stats['Team Score'].mean():.0f}")

        st.markdown("---")

        # ── Score per game (line + markers + star + streak) ──────────────────
        best_idx    = df_stats["Team Score"].idxmax()
        results_list = df_stats["Won"].tolist()
        games        = df_stats["Game"].tolist()
        scores       = df_stats["Team Score"].tolist()

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

        fig_scores = go.Figure()
        for idx in range(len(games) - 1):
            c1, c2  = streak_colour[idx], streak_colour[idx + 1]
            seg_col = c1 if c1 == c2 and c1 != "lightgray" else "lightgray"
            fig_scores.add_trace(go.Scatter(
                x=[games[idx], games[idx + 1]], y=[scores[idx], scores[idx + 1]],
                mode="lines", line=dict(color=seg_col, width=2),
                showlegend=False, hoverinfo="skip",
            ))

        for result, colour in [("Win", "#2ecc71"), ("Loss", "#e74c3c")]:
            mask = (df_stats["Result"] == result) & (df_stats.index != best_idx)
            fig_scores.add_trace(go.Scatter(
                x=df_stats[mask]["Game"], y=df_stats[mask]["Team Score"],
                mode="markers", name=result, marker=dict(color=colour, size=12),
            ))

        best_row    = df_stats.loc[best_idx]
        star_colour = "#2ecc71" if best_row["Won"] else "#e74c3c"
        fig_scores.add_trace(go.Scatter(
            x=[best_row["Game"]], y=[best_row["Team Score"]],
            mode="markers", name="Best Game",
            marker=dict(color=star_colour, size=18, symbol="star"),
        ))

        fig_scores.update_layout(
            title="Team Score per Game",
            xaxis_title=None, yaxis_title="Team Score",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            legend_title=None,
        )

        # ── Score contribution ──────────────────
        contrib_data = pd.DataFrame({
            "Player": [player_1, player_2],
            "Avg Score": [
                df_results[(df_results["player"] == p) & (df_results["game_id"].isin(game_ids))]["score"].sum() / n_games
                for p in [player_1, player_2]
            ],
        })
        fig_contrib = px.pie(
            contrib_data, names="Player", values="Avg Score",
            color_discrete_sequence=["#3498db", "#9b59b6"],
            title="Avg Score Contribution per Game",
        )

        fig_contrib.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=400,
        )

        st.plotly_chart(fig_scores,  use_container_width=True)
        st.plotly_chart(fig_contrib, use_container_width=True)

        st.markdown("---")

        # ── Meld stats | Other stats ─────────────────────────────────────────
        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader("Meld Stats")
            st.metric("Avg Melds / Game",    f"{df_stats['Melds'].mean():.1f}")
            st.metric("Avg Meld Size",        f"{avg_meld_size:.1f} cards")
            st.metric("Avg Canastas / Game",  f"{canastas_per_game:.1f}")

        with col_right:
            st.subheader("Other Stats")
            st.metric("Avg Wild Cards / Game",      f"{wild_per_game:.1f}")
            st.metric("Avg Red Threes / Game",      f"{rt_per_game:.1f}")
            st.metric("Avg Points Deducted / Game", f"{deduct_per_game:.0f}")

        st.markdown("---")

        # ── Cards played chart ───────────────────────────────────────────────
        st.subheader("Cards Played")
        card_stats = pd.DataFrame({
            "Card": CARD_ORDER,
            "Times Melded": [int((pair_melds["base_card"] == c).sum()) for c in CARD_ORDER],
            "Avg Cards in Meld": [
                round(pair_melds[pair_melds["base_card"] == c]["total_cards"].mean(), 1)
                if (pair_melds["base_card"] == c).any() else 0
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
            xaxis_title=None, xaxis_type="category",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_colorbar=dict(title="Avg Cards"),
        )
        st.plotly_chart(fig_cards, use_container_width=True)

        st.markdown("---")

        # ── Game results table ───────────────────────────────────────────────
        st.subheader("Game Results")
        st.dataframe(
            df_stats[["Game", "Team Score", "Opp Score", "Result"]],
            hide_index=True, use_container_width=True,
        )

render_sidebar()
