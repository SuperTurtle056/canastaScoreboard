import streamlit as st
import sqlite3
import pandas as pd
from utils import render_sidebar

def get_connection():
    return sqlite3.connect("canasta.db", check_same_thread=False)

conn = get_connection()
c = conn.cursor()

st.title("Awards")

df_awards    = pd.read_sql("SELECT * FROM awards", conn)
df_melds     = pd.read_sql("SELECT * FROM melds", conn)
df_red_three = pd.read_sql("SELECT * FROM red_threes", conn)
df_deduct    = pd.read_sql("SELECT * FROM deductions", conn)
df_results   = pd.read_sql("SELECT * FROM game_results", conn)

for df in [df_awards, df_melds, df_red_three, df_deduct, df_results]:
    df["game_id"] = df["game_id"].astype(int)

games_played = df_results.groupby("player")["game_id"].count().rename("games_played")

columns = [row[1] for row in c.execute("PRAGMA table_info(awards)").fetchall()]
award_columns = [col for col in columns if col not in ("id", "game_id")]
award_labels  = {col: col.replace("_", " ").title() for col in award_columns}

# higher_is_better = False only for the_hermit (fewest deductions wins)
lower_is_better = {"the_hermit"}

def compute_metric(award_col, game_id, player):
    gm = df_melds[(df_melds["game_id"] == game_id) & (df_melds["player"] == player)]
    gt = df_red_three[(df_red_three["game_id"] == game_id) & (df_red_three["player"] == player)]
    gd = df_deduct[(df_deduct["game_id"] == game_id) & (df_deduct["player"] == player)]

    if award_col == "the_emperor":
        return int(df_results.loc[(df_results["game_id"] == game_id) & (df_results["player"] == player), "score"].sum())

    if award_col == "the_high_priestess":
        best = float("-inf")
        for rid in gm["round_id"].unique():
            ms = gm[gm["round_id"] == rid]["score"].sum()
            rt = gt[gt["round_id"] == rid]["card_count"].sum() * 100
            de = gd[gd["round_id"] == rid]["points_lost"].sum()
            rs = ms + rt - de if ms > 0 else ms - rt - de
            best = max(best, rs)
        return int(best) if best != float("-inf") else 0

    if award_col == "the_magician":
        return int(gt["card_count"].sum())

    if award_col == "the_chariot":
        all_rounds  = set(gm["round_id"].unique())
        with_deduct = set(gd["round_id"].unique())
        return len(all_rounds - with_deduct)

    if award_col == "the_hermit":
        return int(gd["points_lost"].sum())

    if award_col == "the_hierophant":
        return int(gm["twos"].sum() + gm["jokers"].sum())

    if award_col == "the_fool":
        return int(gm["jokers"].sum())

    return 0

award_descriptions = {
    "the_emperor":       "Awarded to the player with the most points across the whole game.",
    "the_high_priestess":"Awarded to the player with the highest scoring single round.",
    "the_magician":      "Awarded to the player who collected the most red threes.",
    "the_chariot":       "Awarded to the player who went out the most times (rounds with no deductions).",
    "the_hermit":        "Awarded to the player who lost the fewest points to deductions.",
    "the_hierophant":    "Awarded to the player who played the most wild cards (twos and jokers combined).",
    "the_fool":          "Awarded to the player who played the most jokers.",
}

selected = st.selectbox("", award_columns, format_func=lambda col: award_labels[col])
st.caption(award_descriptions.get(selected, ""))

rows = []
for _, row in df_awards.iterrows():
    player = row[selected]
    if pd.notna(player):
        rows.append({"player": player, "game_id": row["game_id"], "metric": compute_metric(selected, row["game_id"], player)})

df_metrics = pd.DataFrame(rows)

if df_metrics.empty:
    st.info("No data for this award yet.")
else:
    win_counts = df_awards[selected].value_counts()
    best_per_player = (
        df_metrics.groupby("player")["metric"].min()
        if selected in lower_is_better
        else df_metrics.groupby("player")["metric"].max()
    )

    table_rows = []
    for player in games_played.index:
        played = int(games_played[player])
        wins   = int(win_counts.get(player, 0))
        rate   = round(wins / played, 2) if played > 0 else 0.0
        best   = int(best_per_player[player]) if player in best_per_player.index else None
        table_rows.append({"Player": player, "Wins": wins, "Win Rate": rate, "Best Score": best})

    df_table = pd.DataFrame(table_rows)
    sort_col = st.selectbox("Sort by", df_table.columns[1:], index=0)
    df_table = df_table.sort_values(sort_col, ascending=False).reset_index(drop=True)
    st.dataframe(df_table, hide_index=True, use_container_width=True)

render_sidebar()
