"""Download tool for studio artifacts."""

from google.adk.tools import ToolContext
from notebooklm_agent.helpers import run_nlm


def _profile(ctx: ToolContext) -> str:
    return ctx.state.get("profile", "default")


def download_artifact(
    tool_context: ToolContext,
    notebook_id: str,
    artifact_type: str,
    output_path: str,
) -> dict:
    """Download a studio artifact to a local file.

    Args:
        notebook_id: The notebook's UUID.
        artifact_type: Type of artifact to download. One of:
            audio, video, slide-deck, infographic, report,
            mind-map, data-table, quiz, flashcards.
        output_path: Local file path to save the download.
    """
    return run_nlm(
        ["download", artifact_type, notebook_id, "--output", output_path, "--no-progress"],
        profile=_profile(tool_context),
        json_output=False,
        timeout=300,
    )
