"""
main.py
Gmail JobTracker — unified entry point.

Usage:
    python main.py              # full pipeline: fetch → analyze → serve
    python main.py --serve      # skip fetch/analyze, just start API server
    python main.py --sync       # fetch + analyze only, no server
"""

from __future__ import annotations

import argparse
import subprocess
import sys

from config import API_HOST, API_PORT


def run_sync():
    """Fetch new emails from Gmail and analyze with Ollama."""
    from db.database import get_unanalyzed_emails, init_db
    from gmail.fetcher import fetch_emails
    from llm.analyzer import analyze_all

    print("=" * 60)
    print("  Gmail JobTracker — Sync Pipeline")
    print("=" * 60)

    # Step 0: Init DB
    init_db()

    # Step 1: Fetch emails
    print("\n[1/2] Fetching emails from Gmail...")
    new_count, skip_count = fetch_emails()
    print(f"       → {new_count} new, {skip_count} skipped")

    # Step 2: Analyze
    unanalyzed = len(get_unanalyzed_emails())
    if unanalyzed > 0:
        print(f"\n[2/2] Analyzing {unanalyzed} emails with Ollama...")
        analyze_all()
    else:
        print("\n[2/2] No unanalyzed emails. Skipping.")

    print("\n✔ Sync complete.")


def run_server():
    """Start the FastAPI server via uvicorn."""
    print("=" * 60)
    print("  Gmail JobTracker — API Server")
    print(f"  http://{API_HOST}:{API_PORT}")
    print("=" * 60)

    subprocess.run(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "api.server:app",
            "--host",
            API_HOST,
            "--port",
            str(API_PORT),
            "--reload",
        ]
    )


def main():
    parser = argparse.ArgumentParser(description="Gmail JobTracker")
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Start API server only (skip fetch/analyze)",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Fetch + analyze only (no server)",
    )
    args = parser.parse_args()

    if args.serve:
        run_server()
    elif args.sync:
        run_sync()
    else:
        # Full pipeline: sync then serve
        run_sync()
        print()
        run_server()


if __name__ == "__main__":
    main()
