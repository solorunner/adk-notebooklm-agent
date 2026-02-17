"""Studio artifact creation and management tools."""

from google.adk.tools import ToolContext
from notebooklm_agent.helpers import run_nlm


def _profile(ctx: ToolContext) -> str:
    return ctx.state.get("profile", "default")


def _create_artifact(
    tool_context: ToolContext,
    artifact_type: str,
    notebook_id: str,
    extra_args: list[str] | None = None,
) -> dict:
    args = [artifact_type, "create", notebook_id, "--confirm"]
    if extra_args:
        args.extend(extra_args)
    return run_nlm(
        args,
        profile=_profile(tool_context),
        json_output=False,
        timeout=180,
    )


def create_audio(tool_context: ToolContext, notebook_id: str) -> dict:
    """Create an audio overview (podcast) from notebook sources.

    Args:
        notebook_id: The notebook's UUID.
    """
    return _create_artifact(tool_context, "audio", notebook_id)


def create_video(tool_context: ToolContext, notebook_id: str) -> dict:
    """Create a video overview from notebook sources.

    Args:
        notebook_id: The notebook's UUID.
    """
    return _create_artifact(tool_context, "video", notebook_id)


def create_mindmap(tool_context: ToolContext, notebook_id: str) -> dict:
    """Create a mind map from notebook sources.

    Args:
        notebook_id: The notebook's UUID.
    """
    return _create_artifact(tool_context, "mindmap", notebook_id)


def create_infographic(tool_context: ToolContext, notebook_id: str) -> dict:
    """Create an infographic from notebook sources.

    Args:
        notebook_id: The notebook's UUID.
    """
    return _create_artifact(tool_context, "infographic", notebook_id)


def create_slides(tool_context: ToolContext, notebook_id: str) -> dict:
    """Create a slide deck from notebook sources.

    Args:
        notebook_id: The notebook's UUID.
    """
    return _create_artifact(tool_context, "slides", notebook_id)


def create_data_table(
    tool_context: ToolContext, notebook_id: str, description: str
) -> dict:
    """Create a data table from notebook sources.

    Args:
        notebook_id: The notebook's UUID.
        description: Description of the data table to create.
    """
    return _create_artifact(
        tool_context, "data-table", notebook_id, extra_args=[description]
    )


def create_report(tool_context: ToolContext, notebook_id: str) -> dict:
    """Create a report from notebook sources.

    Args:
        notebook_id: The notebook's UUID.
    """
    return _create_artifact(tool_context, "report", notebook_id)


def create_quiz(tool_context: ToolContext, notebook_id: str) -> dict:
    """Create a quiz from notebook sources.

    Args:
        notebook_id: The notebook's UUID.
    """
    return _create_artifact(tool_context, "quiz", notebook_id)


def create_flashcards(tool_context: ToolContext, notebook_id: str) -> dict:
    """Create flashcards from notebook sources.

    Args:
        notebook_id: The notebook's UUID.
    """
    return _create_artifact(tool_context, "flashcards", notebook_id)


def studio_status(tool_context: ToolContext, notebook_id: str) -> dict:
    """Check the status of all studio artifacts in a notebook.

    Args:
        notebook_id: The notebook's UUID.
    """
    return run_nlm(
        ["studio", "status", notebook_id], profile=_profile(tool_context)
    )


def delete_artifact(
    tool_context: ToolContext, notebook_id: str, artifact_id: str
) -> dict:
    """Delete a studio artifact permanently. This cannot be undone.

    Args:
        notebook_id: The notebook's UUID.
        artifact_id: The artifact's UUID.
    """
    return run_nlm(
        ["studio", "delete", notebook_id, artifact_id, "--confirm"],
        profile=_profile(tool_context),
        json_output=False,
    )
