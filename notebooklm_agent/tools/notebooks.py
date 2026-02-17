"""Notebook management tools."""

from google.adk.tools import ToolContext
from notebooklm_agent.helpers import run_nlm


def _profile(ctx: ToolContext) -> str:
    return ctx.state.get("profile", "default")


def list_notebooks(tool_context: ToolContext) -> dict:
    """List all notebooks in the user's NotebookLM account."""
    return run_nlm(["notebook", "list"], profile=_profile(tool_context))


def create_notebook(tool_context: ToolContext, name: str) -> dict:
    """Create a new notebook.

    Args:
        name: Title for the new notebook.
    """
    result = run_nlm(
        ["notebook", "create", name],
        profile=_profile(tool_context),
        json_output=False,
    )
    return result


def get_notebook(tool_context: ToolContext, notebook_id: str) -> dict:
    """Get details for a specific notebook.

    Args:
        notebook_id: The notebook's UUID.
    """
    return run_nlm(
        ["notebook", "get", notebook_id], profile=_profile(tool_context)
    )


def rename_notebook(
    tool_context: ToolContext, notebook_id: str, new_name: str
) -> dict:
    """Rename an existing notebook.

    Args:
        notebook_id: The notebook's UUID.
        new_name: The new title for the notebook.
    """
    return run_nlm(
        ["notebook", "rename", notebook_id, new_name],
        profile=_profile(tool_context),
        json_output=False,
    )


def delete_notebook(tool_context: ToolContext, notebook_id: str) -> dict:
    """Delete a notebook permanently. This cannot be undone.

    Args:
        notebook_id: The notebook's UUID.
    """
    return run_nlm(
        ["notebook", "delete", notebook_id, "--confirm"],
        profile=_profile(tool_context),
        json_output=False,
    )


def query_notebook(
    tool_context: ToolContext,
    notebook_id: str,
    question: str,
    conversation_id: str = "",
) -> dict:
    """Ask a question against the notebook's sources (RAG query).

    Args:
        notebook_id: The notebook's UUID.
        question: The question to ask.
        conversation_id: Optional conversation ID for follow-up questions.
            If empty, starts a new conversation.
    """
    args = ["notebook", "query", notebook_id, question]
    if conversation_id:
        args += ["-c", conversation_id]

    result = run_nlm(args, profile=_profile(tool_context))

    # Persist conversation_id for follow-ups
    if isinstance(result, dict) and "conversation_id" in result:
        tool_context.state["conversation_id"] = result["conversation_id"]
    if isinstance(result, dict) and not result.get("error"):
        tool_context.state["active_notebook_id"] = notebook_id

    return result
