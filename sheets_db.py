"""
sheets_db.py — shared Google Sheets data layer
Used by both quiz.py and admin.py
"""

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime, timezone, timedelta

EAT = timezone(timedelta(hours=3))

SHEET_ID = "1gXfI_jZ7YAbaVz691HJrXkFKkILZ2nBeireP3dAWxg0"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

COLUMNS = [
    "AttemptID",
    "Name",
    "Email",
    "Gender",
    "Score",
    "AccuratePercentileVerified",
    "RoughPercentileAllAttempts",
    "IsAnonymous",
    "CompletedAt",
    "BrevoMessageID",
    "BrevoUUID",
    "BrevoTags",
    "BrevoSubject",
    "BrevoStatus",
    "BrevoEvent",
    "BrevoEventAt",
    "BrevoReason",
    "BrevoWebhookEmail",
    "BrevoWebhookID",
]


def get_sheet():
    """Return the first worksheet of the results spreadsheet."""
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES,
    )
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).sheet1


@st.cache_data(ttl=60)
def load_results():
    """Load all rows from Google Sheets as a DataFrame."""
    sheet = get_sheet()
    records = sheet.get_all_records(expected_headers=COLUMNS)
    if not records:
        df = pd.DataFrame(columns=COLUMNS)
    else:
        df = pd.DataFrame(records)

    # Ensure all expected columns exist
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""

    # Type coercions
    df["Email"] = df["Email"].fillna("").astype(str).str.strip().str.lower()
    df["Score"] = pd.to_numeric(df["Score"], errors="coerce")
    df["CompletedAt"] = pd.to_datetime(df["CompletedAt"], errors="coerce")

    return df


def invalidate_cache():
    load_results.clear()
    if hasattr(get_verified_stats, "clear"):
        get_verified_stats.clear()


def save_attempt(
    attempt_id,
    name="",
    email="",
    gender="",
    score=None,
    accurate_percentile=None,
    rough_percentile=None,
    brevo_message_id="",
    brevo_uuid="",
    brevo_tags="",
    brevo_subject="",
    brevo_status="",
    brevo_event="",
    brevo_event_at="",
    brevo_reason="",
    brevo_webhook_email="",
    brevo_webhook_id="",
):
    sheet = get_sheet()
    clean_email = str(email).strip().lower()

    new_row = [
        str(attempt_id),
        str(name),
        clean_email,
        str(gender),
        score if score is not None else "",
        accurate_percentile if accurate_percentile is not None else "",
        rough_percentile if rough_percentile is not None else "",
        str(clean_email == ""),   # IsAnonymous
        datetime.now(timezone.utc).astimezone(EAT).strftime("%Y-%m-%d %H:%M:%S"),
        str(brevo_message_id),
        str(brevo_uuid),
        str(brevo_tags),
        str(brevo_subject),
        str(brevo_status),
        str(brevo_event),
        str(brevo_event_at),
        str(brevo_reason),
        str(brevo_webhook_email),
        str(brevo_webhook_id),
    ]

    # Check if this attempt already exists — update it if so
    all_values = sheet.col_values(1)  # AttemptID is column 1
    try:
        row_index = all_values.index(str(attempt_id)) + 1  # 1-based
        sheet.update(f"A{row_index}", [new_row])
    except ValueError:
        # Not found — append as new row
        sheet.append_row(new_row, value_input_option="USER_ENTERED")

    invalidate_cache()


def update_attempt_from_webhook(
    attempt_id="",
    message_id="",
    event="",
    status="",
    event_at="",
    reason="",
    webhook_email="",
    webhook_id="",
    brevo_uuid="",
):
    sheet = get_sheet()

    # Map column names to their 1-based index in the sheet
    col_map = {col: i + 1 for i, col in enumerate(COLUMNS)}

    row_index = None
    all_attempt_ids = sheet.col_values(col_map["AttemptID"])
    if attempt_id:
        try:
            row_index = all_attempt_ids.index(str(attempt_id)) + 1
        except ValueError:
            pass

    if row_index is None and message_id:
        all_message_ids = sheet.col_values(col_map["BrevoMessageID"])
        try:
            row_index = all_message_ids.index(str(message_id)) + 1
        except ValueError:
            pass

    if row_index is None:
        return False

    updates = {
        "BrevoEvent": event,
        "BrevoStatus": status,
        "BrevoEventAt": event_at,
        "BrevoReason": reason,
        "BrevoWebhookEmail": webhook_email,
        "BrevoWebhookID": webhook_id,
        "BrevoUUID": brevo_uuid,
    }

    for col_name, value in updates.items():
        if value:
            col_letter = chr(ord("A") + col_map[col_name] - 1)
            sheet.update(f"{col_letter}{row_index}", [[value]])

    invalidate_cache()
    return True


def delete_all_results():
    """Clear all data rows, keeping the header row intact."""
    sheet = get_sheet()
    # Get total number of rows
    all_values = sheet.get_all_values()
    if len(all_values) <= 1:
        return  # Nothing to delete beyond the header
    # Delete from row 2 downward
    sheet.delete_rows(2, len(all_values))
    invalidate_cache()


@st.cache_data(ttl=60)
def get_verified_stats(gender, current_score):
    """Returns (pool_count, percentile_or_None) for the given gender."""
    df = load_results()
    if df.empty:
        return 0, None

    verified = df[df["Email"] != ""].copy()
    if verified.empty:
        return 0, None

    latest = (
        verified
        .sort_values("CompletedAt")
        .groupby("Email", as_index=False)
        .tail(1)
    )
    pool = latest[(latest["Gender"] == gender) & (latest["Score"].notna())]
    pool_count = len(pool)

    if pool_count < 5:
        return pool_count, None

    lower_count = (pool["Score"] < current_score).sum()
    percentile = round((lower_count / pool_count) * 100)
    return pool_count, percentile