"""
gmail/fetcher.py
Fetch emails from Gmail API and store them in the database.
"""

import base64
from datetime import datetime

from config import GMAIL_BODY_MAX_LENGTH, GMAIL_DEFAULT_MAX_RESULTS, GMAIL_DEFAULT_QUERY
from db.database import get_conn, insert_email
from gmail.auth import get_service


def get_body(payload):
    """Recursively extract plain text body from email payload."""
    if payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode(
            "utf-8", errors="replace"
        )
    for part in payload.get("parts", []):
        if part["mimeType"] == "text/plain" and part["body"].get("data"):
            return base64.urlsafe_b64decode(part["body"]["data"]).decode(
                "utf-8", errors="replace"
            )
    for part in payload.get("parts", []):
        result = get_body(part)
        if result:
            return result
    return ""


def get_header(headers, name):
    """Extract a specific header value from email headers."""
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def fetch_emails(query=GMAIL_DEFAULT_QUERY, max_results=GMAIL_DEFAULT_MAX_RESULTS):
    """
    Fetch emails from Gmail and insert into database.
    Returns (new_count, skip_count).

    Args:
        query: Gmail search query (same syntax as Gmail search bar)
        max_results: Maximum number of emails to fetch
    """
    service = get_service()
    new_count = 0
    skip_count = 0
    next_page = None

    print(f"Fetching emails with query: '{query}' (max {max_results})")

    while (new_count + skip_count) < max_results:
        result = (
            service.users()
            .messages()
            .list(
                userId="me",
                q=query,
                maxResults=min(100, max_results - new_count - skip_count),
                pageToken=next_page,
            )
            .execute()
        )

        msgs = result.get("messages", [])
        if not msgs:
            break

        for msg in msgs:
            conn = get_conn()
            exists = conn.execute(
                "SELECT 1 FROM emails WHERE gmail_id = ?", (msg["id"],)
            ).fetchone()
            conn.close()

            if exists:
                skip_count += 1
                continue

            detail = (
                service.users()
                .messages()
                .get(userId="me", id=msg["id"], format="full")
                .execute()
            )

            headers = detail.get("payload", {}).get("headers", [])
            body = get_body(detail.get("payload", {}))
            body = body[:GMAIL_BODY_MAX_LENGTH] if body else ""

            ts = int(detail.get("internalDate", 0)) / 1000
            date_str = (
                datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else ""
            )

            email = {
                "gmail_id": detail["id"],
                "date": date_str,
                "sender": get_header(headers, "From"),
                "recipient": get_header(headers, "To"),
                "subject": get_header(headers, "Subject"),
                "snippet": detail.get("snippet", ""),
                "body": body.replace("\r", ""),
                "labels": ", ".join(detail.get("labelIds", [])),
            }

            inserted = insert_email(email)
            if inserted:
                new_count += 1
                print(
                    f"  [{new_count}] {email['date']} | {email['sender'][:30]} | {email['subject'][:50]}"
                )
            else:
                skip_count += 1

        next_page = result.get("nextPageToken")
        if not next_page:
            break

    print(
        f"\nDone. {new_count} new emails stored, {skip_count} skipped (already in DB)"
    )
    return new_count, skip_count


if __name__ == "__main__":
    fetch_emails()
