from fastapi import FastAPI, Request, Header
from fastapi.responses import JSONResponse
import pandas as pd
import os

CSV_PATH = "quiz_results.csv"

app = FastAPI()


def load_results(csv_path=CSV_PATH):
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
        except pd.errors.EmptyDataError:
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()

    required_cols = [
        "AttemptID",
        "Name",
        "Email",
        "Gender",
        "Score",
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

    for col in required_cols:
        if col not in df.columns:
            df[col] = ""

    return df


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
    csv_path=CSV_PATH
):
    df = load_results(csv_path)

    row_index = None

    if attempt_id:
        matches = df.index[df["AttemptID"].astype(str) == str(attempt_id)]
        if len(matches) > 0:
            row_index = matches[0]

    if row_index is None and message_id:
        matches = df.index[df["BrevoMessageID"].astype(str) == str(message_id)]
        if len(matches) > 0:
            row_index = matches[0]

    if row_index is None:
        return False

    if event:
        df.at[row_index, "BrevoEvent"] = event
    if status:
        df.at[row_index, "BrevoStatus"] = status
    if event_at:
        df.at[row_index, "BrevoEventAt"] = event_at
    if reason:
        df.at[row_index, "BrevoReason"] = reason
    if webhook_email:
        df.at[row_index, "BrevoWebhookEmail"] = webhook_email
    if webhook_id:
        df.at[row_index, "BrevoWebhookID"] = webhook_id
    if brevo_uuid:
        df.at[row_index, "BrevoUUID"] = brevo_uuid

    df.to_csv(csv_path, index=False)
    return True


@app.post("/brevo-webhook")
async def brevo_webhook(
    request: Request,
    x_mailin_custom: str | None = Header(default=None)
):
    payload = await request.json()

    # Brevo usually sends a list for batched webhook events
    events = payload if isinstance(payload, list) else [payload]

    updated = 0

    for item in events:
        event = item.get("event", "")
        email = (item.get("email") or "").strip().lower()
        message_id = item.get("message-id", "") or item.get("messageId", "")
        event_at = item.get("date", "") or item.get("ts_event", "")
        reason = (
            item.get("reason", "")
            or item.get("tag", "")
            or item.get("message", "")
        )
        brevo_uuid = item.get("id", "") or item.get("uuid", "")

        # Try to recover AttemptID from Brevo custom headers if present
        attempt_id = ""

        headers_obj = item.get("X-Mailin-custom") or item.get("headers") or {}
        if isinstance(headers_obj, dict):
            attempt_id = (
                headers_obj.get("X-Quiz-Attempt-ID", "")
                or headers_obj.get("X-Entity-Ref-ID", "")
            )

        # fallback if header came as raw string
        if not attempt_id and isinstance(x_mailin_custom, str):
            # Example raw style: "X-Quiz-Attempt-ID: abc123|X-Entity-Ref-ID: abc123"
            for part in x_mailin_custom.split("|"):
                if "X-Quiz-Attempt-ID" in part:
                    attempt_id = part.split(":", 1)[-1].strip()
                    break

        status_map = {
            "sent": "sent",
            "delivered": "delivered",
            "opened": "opened",
            "click": "clicked",
            "clicked": "clicked",
            "hardBounce": "hard_bounced",
            "softBounce": "soft_bounced",
            "blocked": "blocked",
            "error": "error",
            "deferred": "deferred",
            "spam": "spam",
            "invalid": "invalid",
            "unsubscribed": "unsubscribed",
        }

        status = status_map.get(event, event)

        ok = update_attempt_from_webhook(
            attempt_id=attempt_id,
            message_id=message_id,
            event=event,
            status=status,
            event_at=event_at,
            reason=reason,
            webhook_email=email,
            webhook_id=attempt_id,
            brevo_uuid=brevo_uuid,
        )

        if ok:
            updated += 1

    return JSONResponse({"ok": True, "updated": updated})