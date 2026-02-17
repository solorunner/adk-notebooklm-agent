"""Research tools for discovering new sources."""

from google.adk.tools import ToolContext
from notebooklm_agent.helpers import run_nlm


def _profile(ctx: ToolContext) -> str:
    return ctx.state.get("profile", "default")


def start_research(
    tool_context: ToolContext, notebook_id: str, query: str
) -> dict:
    """Start a research task to discover new sources from the web.

    Args:
        notebook_id: The notebook's UUID to add discovered sources to.
        query: What to search for.
    """
    return run_nlm(
        ["research", "start", query, "--notebook-id", notebook_id],
        profile=_profile(tool_context),
        json_output=False,
        timeout=180,
    )


def research_status(tool_context: ToolContext, notebook_id: str) -> dict:
    """Check research task progress for a notebook.

    Args:
        notebook_id: The notebook's UUID.
    """
    return run_nlm(
        ["research", "status", notebook_id, "--max-wait", "0"],
        profile=_profile(tool_context),
        json_output=False,
    )


def import_research(tool_context: ToolContext, notebook_id: str) -> dict:
    """Import discovered sources from a completed research task into the notebook.

    Args:
        notebook_id: The notebook's UUID.
    """
    return run_nlm(
        ["research", "import", notebook_id],
        profile=_profile(tool_context),
        json_output=False,
        timeout=300,
    )
