import streamlit as st
import os
import pandas as pd

st.set_page_config(layout="centered", page_title="Admin Dashboard")

def check_password():
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    if st.session_state.admin_authenticated:
        return True

    password = st.text_input("Enter admin password", type="password")

    if st.button("Login"):
        if password == st.secrets["admin_password"]:
            st.session_state.admin_authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")

    return False

if not check_password():
    st.stop()

CSV_PATH = "quiz_results.csv"

st.title("Admin Dashboard")

if not os.path.exists(CSV_PATH):
    st.warning("No quiz results found yet.")
    st.stop()

df = pd.read_csv(CSV_PATH)

required_cols = [
    "AttemptID",
    "Name",
    "Email",
    "Gender",
    "Score",
    "IsAnonymous",
    "CompletedAt",
    "RoughPercentileAllAttempts",
    "AccuratePercentileVerified",
]

for col in required_cols:
    if col not in df.columns:
        df[col] = ""

df["Email"] = df["Email"].fillna("").astype(str).str.strip().str.lower()
df["Score"] = pd.to_numeric(df["Score"], errors="coerce")
df["CompletedAt"] = pd.to_datetime(df["CompletedAt"], errors="coerce")

verified_df = df[df["Email"] != ""].copy()
anonymous_df = df[df["Email"] == ""].copy()

verified_latest = pd.DataFrame()
if not verified_df.empty:
    verified_latest = verified_df.sort_values("CompletedAt").groupby("Email", as_index=False).tail(1)

st.subheader("Top-level stats")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total attempts", len(df))
col2.metric("Anonymous attempts", len(anonymous_df))
col3.metric("Verified attempts", len(verified_df))
col4.metric("Verified users (latest)", len(verified_latest))

st.markdown("---")
st.subheader("Score stats")

score_df = df.dropna(subset=["Score"]).copy()

if not score_df.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("Average score (all attempts)", round(score_df["Score"].mean(), 1))
    col2.metric("Lowest score", int(score_df["Score"].min()))
    col3.metric("Highest score", int(score_df["Score"].max()))
else:
    st.info("No score data yet.")

st.markdown("---")
st.subheader("By gender")

if not score_df.empty:
    gender_summary = (
        score_df.groupby("Gender")
        .agg(
            Attempts=("Score", "count"),
            AverageScore=("Score", "mean"),
            MinScore=("Score", "min"),
            MaxScore=("Score", "max"),
        )
        .reset_index()
    )
    gender_summary["AverageScore"] = gender_summary["AverageScore"].round(1)
    st.dataframe(gender_summary, use_container_width=True)
else:
    st.info("No gender summary available yet.")

st.markdown("---")
st.subheader("Verified latest users only")

if not verified_latest.empty:
    verified_gender_summary = (
        verified_latest.groupby("Gender")
        .agg(
            VerifiedUsers=("Score", "count"),
            AverageScore=("Score", "mean"),
            MinScore=("Score", "min"),
            MaxScore=("Score", "max"),
        )
        .reset_index()
    )
    verified_gender_summary["AverageScore"] = verified_gender_summary["AverageScore"].round(1)
    st.dataframe(verified_gender_summary, use_container_width=True)
else:
    st.info("No verified users yet.")

st.markdown("---")
st.subheader("Recent attempts")

recent_cols = [
    "CompletedAt",
    "AttemptID",
    "Name",
    "Email",
    "Gender",
    "Score",
    "IsAnonymous",
    "RoughPercentileAllAttempts",
    "AccuratePercentileVerified",
]

recent_df = df[recent_cols].sort_values("CompletedAt", ascending=False)
st.dataframe(recent_df, use_container_width=True)

st.markdown("---")
st.subheader("Latest verified users")

if not verified_latest.empty:
    latest_cols = [
        "CompletedAt",
        "AttemptID",
        "Name",
        "Email",
        "Gender",
        "Score",
        "AccuratePercentileVerified",
    ]
    st.dataframe(
        verified_latest[latest_cols].sort_values("CompletedAt", ascending=False),
        use_container_width=True
    )
else:
    st.info("No verified user records yet.")

confirm = st.checkbox("I understand this will permanently delete all quiz data")

if confirm and st.button("Delete all quiz data"):
    if os.path.exists("quiz_results.csv"):
        os.remove("quiz_results.csv")
    st.success("quiz_results.csv deleted.")
    st.rerun()