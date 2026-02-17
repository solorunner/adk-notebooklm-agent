"""Notebook sharing tools."""

from google.adk.tools import ToolContext
from notebooklm_agent.helpers import run_nlm


def _profile(ctx: ToolContext) -> str:
    return ctx.state.get("profile", "default")


def share_status(tool_context: ToolContext, notebook_id: str) -> dict:
    """Show sharing status and collaborators for a notebook.

    Args:
        notebook_id: The notebook's UUID.
    """
    return run_nlm(
        ["share", "status", notebook_id], profile=_profile(tool_context)
    )


def share_public(tool_context: ToolContext, notebook_id: str) -> dict:
    """Enable public link access for a notebook (anyone with link can view).

    Args:
        notebook_id: The notebook's UUID.
    """
    return run_nlm(
        ["share", "public", notebook_id],
        profile=_profile(tool_context),
        json_output=False,
    )


def share_private(tool_context: ToolContext, notebook_id: str) -> dict:
    """Disable public link access (restricted to collaborators only).

    Args:
        notebook_id: The notebook's UUID.
    """
    return run_nlm(
        ["share", "private", notebook_id],
        profile=_profile(tool_context),
        json_output=False,
    )


def share_invite(
    tool_context: ToolContext, notebook_id: str, email: str
) -> dict:
    """Invite a collaborator to a notebook by email.

    Args:
        notebook_id: The notebook's UUID.
        email: Email address of the person to invite.
    """
    return run_nlm(
        ["share", "invite", notebook_id, email],
        profile=_profile(tool_context),
        json_output=False,
    )
