"""Authentication tools for NotebookLM agent."""

import logging
import secrets
import time

import auth_store

logger = logging.getLogger(__name__)

from google.adk.tools import ToolContext
from notebooklm_agent.helpers import run_nlm, run_nlm_with_tempfile


def _set_auth_valid(tool_context: ToolContext, profile: str):
    """Mark authentication as valid in session state."""
    tool_context.state["profile"] = profile
    tool_context.state["auth_valid"] = True
    tool_context.state["auth_valid_at"] = time.time()


def check_auth(tool_context: ToolContext, profile: str = "fresh_test") -> dict:
    """Check if the nlm CLI is authenticated for the given profile.

    Call this before using any other tool. On success it stores the profile
    in session state so all subsequent tools use it automatically.

    Args:
        profile: The nlm auth profile to check (default: "default").
    """
    result = run_nlm(
        ["login", "--check"],
        profile=profile,
        json_output=False,
    )

    if "error" in result:
        return {
            "authenticated": False,
            "message": "Not authenticated. Call start_auth to begin the authentication flow.",
            "details": result["error"],
        }

    _set_auth_valid(tool_context, profile)
    return {
        "authenticated": True,
        "profile": profile,
        "message": f"Authenticated with profile '{profile}'.",
    }


def start_auth(tool_context: ToolContext) -> dict:
    """Start the authentication flow for NotebookLM.

    Generates a unique auth token and provides instructions for the user
    to authenticate using either the Chrome extension or cookie paste method.
    """
    token = secrets.token_urlsafe(32)
    tool_context.state["auth_token"] = token

    # Register token so the extension can auto-fill it
    auth_store.latest_token["token"] = token
    auth_store.latest_token["created_at"] = time.time()

    return {
        "token": token,
        "message": "Auth token generated. Present the Chrome extension instructions. IMPORTANT: When the user says 'done', call check_auth_token (NOT check_auth).",
        "extension_method": {
            "step1": "Open the install guide: http://localhost:8001/auth/install",
            "step2": "Follow the steps to download and install the extension (one-time setup)",
            "step3": f"Click the extension icon, enter token: {token}",
            "step4": "Click 'Authenticate', then come back and say 'done'",
        },
    }


def check_auth_token(tool_context: ToolContext) -> dict:
    """Check if the Chrome extension has delivered cookies for the current auth token.

    Call this after start_auth when the user says they've clicked Authenticate
    in the extension.
    """
    token = tool_context.state.get("auth_token")
    if not token:
        logger.error("check_auth_token: no auth_token in state")
        return {"error": "No auth token found. Call start_auth first."}

    logger.info("check_auth_token: checking token %s...", token[:8])

    # Access shared auth store directly (same process, avoids HTTP deadlock)
    entry = auth_store.pending_auth.get(token)

    if not entry or "cookies" not in entry:
        logger.info("check_auth_token: cookies not found for token")
        return {
            "ready": False,
            "message": "Cookies not received yet. Ask the user to try again.",
        }

    # Consume the token (remove from pending)
    cookies = auth_store.pending_auth.pop(token, {}).get("cookies", {})
    logger.info("check_auth_token: consumed, got %d cookies", len(cookies))

    # Build cookie string for nlm login --manual
    cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
    profile = tool_context.state.get("profile", "default")

    logger.info("check_auth_token: importing cookies to profile '%s'", profile)
    result = run_nlm_with_tempfile(
        args_before=["login", "--manual"],
        file_content=cookie_str,
        profile=profile,
        json_output=False,
        timeout=30,
    )

    if "error" in result:
        logger.error("check_auth_token: nlm login --manual failed: %s", result["error"])
        return {
            "authenticated": False,
            "message": "Cookie import failed.",
            "details": result["error"],
        }

    _set_auth_valid(tool_context, profile)
    tool_context.state["auth_token"] = None
    logger.info("check_auth_token: SUCCESS")
    return {"authenticated": True, "message": "Authenticated via Chrome extension."}


def import_cookies(
    tool_context: ToolContext,
    cookie_string: str,
    profile: str = "default",
) -> dict:
    """Import cookies pasted by the user to authenticate with NotebookLM.

    Accepts a cURL command, raw cookie header, or semicolon-separated cookie string.
    Use this when the user pastes their cookies from browser DevTools.

    Args:
        cookie_string: A cURL command, Cookie header value, or raw cookie string.
        profile: The nlm auth profile to store cookies in (default: "default").
    """
    result = run_nlm_with_tempfile(
        args_before=["login", "--manual"],
        file_content=cookie_string,
        profile=profile,
        json_output=False,
        timeout=30,
    )

    if "error" in result:
        return {
            "authenticated": False,
            "message": "Cookie import failed.",
            "details": result["error"],
            "suggestion": "Make sure you copied the full cURL command or all 5 required cookies (SID, HSID, SSID, APISID, SAPISID).",
        }

    # Verify cookies work
    verify = run_nlm(["login", "--check"], profile=profile, json_output=False)
    if "error" in verify:
        return {
            "authenticated": False,
            "message": "Cookies imported but verification failed.",
            "details": verify["error"],
        }

    _set_auth_valid(tool_context, profile)
    return {"authenticated": True, "message": "Cookies imported and verified."}
