"""Shared in-memory auth store used by both server.py and agent tools.

This module acts as a singleton — both the server endpoints and the agent
tools import it, and since they run in the same process they share the
same dict instances. This avoids the deadlock that occurs when agent tools
make HTTP requests back to their own server.
"""

import time

# Pending auth tokens → cookies delivered by the Chrome extension
# Key: token string, Value: {"cookies": dict, "received_at": float}
pending_auth: dict[str, dict] = {}

# Latest token registered by start_auth for extension auto-fill
latest_token: dict = {"token": None, "created_at": 0.0}


def cleanup_expired(max_age: int = 600):
    """Remove tokens older than max_age seconds."""
    cutoff = time.time() - max_age
    expired = [k for k, v in pending_auth.items() if v["received_at"] < cutoff]
    for k in expired:
        pending_auth.pop(k, None)
