import streamlit as st

st.set_page_config(layout="centered")

quiz = st.Page(
    "pages/quiz.py",
    title="Quiz",
    icon="🧠",
    default=True,
    url_path=""
)

share = st.Page(
    "pages/share.py",
    title="Share",
    icon="📢",
    url_path="share"
)

explore = st.Page(
    "pages/explore.py",
    title="Explore",
    icon="🔍",
    url_path="explore"
)

admin = st.Page(
    "pages/admin.py",
    title="Admin",
    icon="📊",
    url_path="admin"
)

pg = st.navigation(
    [quiz, share, explore, admin],
    position="hidden"
)

pg.run()