"""Note management tools."""

from google.adk.tools import ToolContext
from notebooklm_agent.helpers import run_nlm


def _profile(ctx: ToolContext) -> str:
    return ctx.state.get("profile", "default")


def list_notes(tool_context: ToolContext, notebook_id: str) -> dict:
    """List all notes in a notebook.

    Args:
        notebook_id: The notebook's UUID.
    """
    return run_nlm(
        ["note", "list", notebook_id], profile=_profile(tool_context)
    )


def create_note(
    tool_context: ToolContext,
    notebook_id: str,
    title: str,
    content: str,
) -> dict:
    """Create a new note in a notebook.

    Args:
        notebook_id: The notebook's UUID.
        title: Title for the note.
        content: Body content for the note.
    """
    return run_nlm(
        ["note", "create", notebook_id, "--title", title, "--content", content],
        profile=_profile(tool_context),
        json_output=False,
    )


def update_note(
    tool_context: ToolContext,
    notebook_id: str,
    note_id: str,
    title: str = "",
    content: str = "",
) -> dict:
    """Update an existing note's title and/or content.

    Args:
        notebook_id: The notebook's UUID.
        note_id: The note's UUID.
        title: New title (leave empty to keep current).
        content: New content (leave empty to keep current).
    """
    args = ["note", "update", notebook_id, note_id]
    if title:
        args += ["--title", title]
    if content:
        args += ["--content", content]
    return run_nlm(
        args, profile=_profile(tool_context), json_output=False
    )


def delete_note(
    tool_context: ToolContext, notebook_id: str, note_id: str
) -> dict:
    """Delete a note permanently. This cannot be undone.

    Args:
        notebook_id: The notebook's UUID.
        note_id: The note's UUID.
    """
    return run_nlm(
        ["note", "delete", notebook_id, note_id],
        profile=_profile(tool_context),
        json_output=False,
    )
