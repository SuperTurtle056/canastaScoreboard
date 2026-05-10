import streamlit as st
import sqlite3
from utils import render_sidebar

def get_connection():
    return sqlite3.connect("canasta.db", check_same_thread=False)

conn = get_connection()
c = conn.cursor()

st.title("Awards")

st.image("images/the_emperor.jpg")



render_sidebar()