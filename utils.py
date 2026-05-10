import streamlit as st

def render_sidebar():
    st.sidebar.page_link('app.py', label='Home')
    st.sidebar.page_link('pages/leaderboard.py', label='Leaderboard')
    st.sidebar.page_link('pages/awards.py', label='Awards')
    st.sidebar.page_link('pages/teamStats.py', label='Team Stats')
    st.sidebar.page_link('pages/continueGame.py', label='Continue Game')
    st.sidebar.page_link('pages/startNewGame.py', label='New Game')
