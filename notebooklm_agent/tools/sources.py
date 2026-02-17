"""Source management tools."""

from google.adk.tools import ToolContext
from notebooklm_agent.helpers import run_nlm


def _profile(ctx: ToolContext) -> str:
    return ctx.state.get("profile", "default")


def list_sources(tool_context: ToolContext, notebook_id: str) -> dict:
    """List all sources in a notebook.

    Args:
        notebook_id: The notebook's UUID.
    """
    return run_nlm(
        ["source", "list", notebook_id], profile=_profile(tool_context)
    )


def add_source_url(
    tool_context: ToolContext,
    notebook_id: str,
    url: str,
    wait: bool = True,
) -> dict:
    """Add a URL (website or YouTube) as a source to a notebook.

    Args:
        notebook_id: The notebook's UUID.
        url: The URL to add.
        wait: Whether to wait for processing to complete (default True).
    """
    args = ["source", "add", notebook_id, "--url", url]
    if wait:
        args.append("--wait")
    return run_nlm(
        args,
        profile=_profile(tool_context),
        json_output=False,
        timeout=300 if wait else 120,
    )


def add_source_file(
    tool_context: ToolContext,
    notebook_id: str,
    file_path: str,
    wait: bool = True,
) -> dict:
    """Add a local file (PDF, text, etc.) as a source to a notebook.

    Args:
        notebook_id: The notebook's UUID.
        file_path: Path to the local file to upload.
        wait: Whether to wait for processing to complete (default True).
    """
    args = ["source", "add", notebook_id, "--file", file_path]
    if wait:
        args.append("--wait")
    return run_nlm(
        args,
        profile=_profile(tool_context),
        json_output=False,
        timeout=300 if wait else 120,
    )


def add_source_text(
    tool_context: ToolContext,
    notebook_id: str,
    text: str,
    title: str = "",
) -> dict:
    """Add inline text as a source to a notebook.

    Args:
        notebook_id: The notebook's UUID.
        text: The text content to add.
        title: Optional title for the source.
    """
    args = ["source", "add", notebook_id, "--text", text]
    if title:
        args += ["--title", title]
    return run_nlm(
        args, profile=_profile(tool_context), json_output=False
    )


def get_source(tool_context: ToolContext, source_id: str) -> dict:
    """Get details for a specific source.

    Args:
        source_id: The source's UUID.
    """
    return run_nlm(
        ["source", "get", source_id], profile=_profile(tool_context)
    )


def describe_source(tool_context: ToolContext, source_id: str) -> dict:
    """Get an AI-generated summary and keywords for a source.

    Args:
        source_id: The source's UUID.
    """
    return run_nlm(
        ["source", "describe", source_id], profile=_profile(tool_context)
    )


def delete_source(tool_context: ToolContext, source_id: str) -> dict:
    """Delete a source permanently. This cannot be undone.

    Args:
        source_id: The source's UUID.
    """
    return run_nlm(
        ["source", "delete", source_id, "--confirm"],
        profile=_profile(tool_context),
        json_output=False,
    )
