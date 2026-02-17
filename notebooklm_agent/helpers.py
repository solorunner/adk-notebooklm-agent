"""Shared subprocess runner for the nlm CLI."""

import json
import os
import shutil
import subprocess
import tempfile

NLM_PATH = shutil.which("nlm") or "nlm"


def run_nlm(
    args: list[str],
    profile: str = "default",
    json_output: bool = True,
    timeout: int = 120,
) -> dict:
    """Execute an nlm CLI command and return parsed output.

    Args:
        args: Command arguments (e.g. ["notebook", "list"]).
        profile: Auth profile name.
        json_output: Whether to append --json flag.
        timeout: Subprocess timeout in seconds.

    Returns:
        dict with either parsed JSON data or {"output": raw_text} on success,
        or {"error": message} on failure.
    """
    cmd = [NLM_PATH] + args + ["--profile", profile]
    if json_output:
        cmd.append("--json")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"error": f"Command timed out after {timeout}s: {' '.join(cmd)}"}
    except FileNotFoundError:
        return {"error": f"nlm CLI not found at {NLM_PATH}. Is it installed?"}

    if result.returncode != 0:
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        msg = stderr or stdout or f"Command failed with exit code {result.returncode}"
        error_result = {"error": msg}
        auth_keywords = ["unauthorized", "401", "auth", "cookie", "session expired", "login required"]
        if any(kw in msg.lower() for kw in auth_keywords):
            error_result["auth_expired"] = True
        return error_result

    stdout = result.stdout.strip()
    if not stdout:
        return {"output": "OK"}

    if json_output:
        try:
            return json.loads(stdout)
        except json.JSONDecodeError:
            return {"output": stdout}

    return {"output": stdout}


def run_nlm_with_tempfile(
    args_before: list[str],
    file_content: str,
    args_after: list[str] | None = None,
    profile: str = "default",
    json_output: bool = False,
    timeout: int = 30,
) -> dict:
    """Run an nlm command that reads input from a temporary file.

    Creates a temp file with file_content, passes it via --file flag,
    then cleans up.

    Args:
        args_before: Command args before --file (e.g. ["login", "--manual"]).
        file_content: Content to write to the temp file.
        args_after: Additional args after the --file path.
        profile: Auth profile name.
        json_output: Whether to append --json flag.
        timeout: Subprocess timeout in seconds.

    Returns:
        dict with parsed output or error.
    """
    fd, path = tempfile.mkstemp(suffix=".txt", prefix="nlm_")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(file_content)
        full_args = args_before + ["--file", path] + (args_after or [])
        return run_nlm(
            full_args,
            profile=profile,
            json_output=json_output,
            timeout=timeout,
        )
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass
