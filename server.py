"""Custom ADK server with auth endpoints for NotebookLM agent."""

import io
import secrets
import time
import zipfile
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from google.adk.cli.fast_api import get_fast_api_app

import auth_store


def create_app() -> FastAPI:
    app = get_fast_api_app(
        agents_dir=".",
        web=True,
        host="0.0.0.0",
        port=8000,
        reload_agents=True,
    )

    # --- Cleanup middleware (must be registered before routes) ---

    @app.middleware("http")
    async def cleanup_tokens(request: Request, call_next):
        cutoff = time.time() - 600  # 10 min expiry
        expired = [k for k, v in auth_store.pending_auth.items() if v["received_at"] < cutoff]
        for k in expired:
            auth_store.pending_auth.pop(k, None)
        return await call_next(request)

    # --- Auth endpoints ---

    @app.post("/auth/cookies")
    async def receive_cookies(request: Request):
        """Receive cookies from Chrome extension."""
        data = await request.json()
        token = data.get("token")
        cookies = data.get("cookies")
        if not token or not cookies:
            return JSONResponse({"error": "token and cookies required"}, 400)
        auth_store.pending_auth[token] = {"cookies": cookies, "received_at": time.time()}
        return {"status": "ok"}

    @app.get("/auth/status/{token}")
    async def auth_status(token: str):
        """Check if cookies have been received for this token."""
        entry = auth_store.pending_auth.get(token)
        if not entry:
            return {"ready": False}
        return {"ready": True, "cookies": entry["cookies"]}

    @app.post("/auth/consume/{token}")
    async def consume_auth(token: str):
        """Consume (delete) a pending auth token after storing cookies."""
        entry = auth_store.pending_auth.pop(token, None)
        if not entry:
            return JSONResponse({"error": "token not found or already consumed"}, 404)
        return {"status": "consumed", "cookies": entry["cookies"]}

    @app.get("/auth/token")
    async def generate_token():
        """Generate a new auth token for the extension flow."""
        token = secrets.token_urlsafe(32)
        return {"token": token}

    @app.post("/auth/register-token")
    async def register_token(request: Request):
        """Register a token so the extension can auto-fill it."""
        data = await request.json()
        token = data.get("token")
        if not token:
            return JSONResponse({"error": "token required"}, 400)
        auth_store.latest_token["token"] = token
        auth_store.latest_token["created_at"] = time.time()
        return {"status": "ok"}

    @app.get("/auth/latest-token")
    async def latest_token():
        """Return the latest auth token for extension auto-fill."""
        if not auth_store.latest_token["token"]:
            return {"token": None}
        # Expire after 10 minutes
        if time.time() - auth_store.latest_token["created_at"] > 600:
            auth_store.latest_token["token"] = None
            return {"token": None}
        return {"token": auth_store.latest_token["token"]}

    # Serve extension as downloadable zip
    ext_dir = Path(__file__).parent / "_extension"

    @app.get("/auth/extension.zip")
    async def download_extension():
        """Serve the Chrome extension as a downloadable zip."""
        if not ext_dir.exists():
            return JSONResponse({"error": "extension directory not found"}, 404)
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in ext_dir.iterdir():
                if f.is_file():
                    zf.write(f, f"notebooklm-auth-helper/{f.name}")
        buf.seek(0)
        return Response(
            content=buf.read(),
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=notebooklm-auth-helper.zip"},
        )

    @app.get("/auth/install", response_class=HTMLResponse)
    async def install_page():
        """Guided Chrome extension install page."""
        return _INSTALL_PAGE_HTML

    # Serve extension files (static, for direct access)
    if ext_dir.exists():
        app.mount(
            "/auth/extension/files",
            StaticFiles(directory=str(ext_dir)),
            name="extension",
        )

    return app


_INSTALL_PAGE_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Install NotebookLM Auth Helper</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #f8f9fa; color: #1a1a1a;
    display: flex; justify-content: center; padding: 40px 16px;
  }
  .card {
    background: #fff; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,.08);
    max-width: 600px; width: 100%; padding: 32px;
  }
  h1 { font-size: 22px; margin-bottom: 8px; }
  .subtitle { color: #666; font-size: 14px; margin-bottom: 28px; }
  .download-btn {
    display: inline-flex; align-items: center; gap: 8px;
    background: #4285f4; color: #fff; border: none; border-radius: 8px;
    padding: 14px 28px; font-size: 16px; font-weight: 600;
    cursor: pointer; text-decoration: none; margin-bottom: 32px;
  }
  .download-btn:hover { background: #3367d6; }
  .download-btn svg { width: 20px; height: 20px; fill: #fff; }
  .steps { counter-reset: step; list-style: none; }
  .steps li {
    counter-increment: step; position: relative;
    padding: 16px 0 16px 52px; border-bottom: 1px solid #eee;
  }
  .steps li:last-child { border-bottom: none; }
  .steps li::before {
    content: counter(step);
    position: absolute; left: 0; top: 16px;
    width: 36px; height: 36px; border-radius: 50%;
    background: #e8f0fe; color: #4285f4;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 15px;
  }
  .steps li.done::before { background: #e6f4ea; color: #137333; content: "\\2713"; }
  .step-title { font-weight: 600; font-size: 15px; margin-bottom: 4px; }
  .step-desc { color: #555; font-size: 13px; line-height: 1.5; }
  code {
    background: #f1f3f4; padding: 2px 6px; border-radius: 4px;
    font-size: 13px; font-family: "SF Mono", Menlo, monospace;
  }
  .test-section {
    margin-top: 28px; padding-top: 24px; border-top: 2px solid #eee;
  }
  .test-btn {
    background: #34a853; color: #fff; border: none; border-radius: 8px;
    padding: 12px 24px; font-size: 15px; font-weight: 600; cursor: pointer;
  }
  .test-btn:hover { background: #2d8e47; }
  .test-btn:disabled { background: #ccc; cursor: default; }
  .test-result {
    margin-top: 12px; padding: 12px; border-radius: 8px;
    font-size: 14px; display: none;
  }
  .test-ok { background: #e6f4ea; color: #137333; display: block; }
  .test-fail { background: #fce8e6; color: #c5221f; display: block; }
  .test-wait { background: #e8f0fe; color: #1967d2; display: block; }
</style>
</head>
<body>
<div class="card">
  <h1>NotebookLM Auth Helper</h1>
  <p class="subtitle">Chrome extension for one-click authentication with the NotebookLM agent</p>

  <a class="download-btn" href="/auth/extension.zip" id="download-btn">
    <svg viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>
    Download Extension
  </a>

  <ol class="steps">
    <li id="step-1">
      <div class="step-title">Unzip the downloaded file</div>
      <div class="step-desc">Extract <code>notebooklm-auth-helper.zip</code> — you'll get a folder called <code>notebooklm-auth-helper</code></div>
    </li>
    <li id="step-2">
      <div class="step-title">Open Chrome Extensions</div>
      <div class="step-desc">Go to <code>chrome://extensions</code> in your browser (copy-paste into address bar)</div>
    </li>
    <li id="step-3">
      <div class="step-title">Enable Developer Mode</div>
      <div class="step-desc">Toggle the <strong>Developer mode</strong> switch in the top-right corner</div>
    </li>
    <li id="step-4">
      <div class="step-title">Load the extension</div>
      <div class="step-desc">Click <strong>Load unpacked</strong> and select the <code>notebooklm-auth-helper</code> folder</div>
    </li>
    <li id="step-5">
      <div class="step-title">You're done!</div>
      <div class="step-desc">Go back to the agent chat. When prompted, click the extension icon in Chrome's toolbar, paste the auth token, and click <strong>Authenticate</strong>.</div>
    </li>
  </ol>

  <div class="test-section">
    <button class="test-btn" id="test-btn">Test Connection</button>
    <div class="test-result" id="test-result"></div>
  </div>
</div>

<script>
  // Track download click
  document.getElementById("download-btn").addEventListener("click", () => {
    document.getElementById("step-1").classList.add("done");
  });

  // Test connection to server
  document.getElementById("test-btn").addEventListener("click", async () => {
    const btn = document.getElementById("test-btn");
    const result = document.getElementById("test-result");
    btn.disabled = true;
    result.className = "test-result test-wait";
    result.style.display = "block";
    result.textContent = "Testing connection...";

    try {
      const resp = await fetch("/auth/token");
      if (resp.ok) {
        result.className = "test-result test-ok";
        result.textContent = "Server is running and reachable. Extension is ready to use!";
      } else {
        result.className = "test-result test-fail";
        result.textContent = "Server responded with an error: " + resp.status;
      }
    } catch (err) {
      result.className = "test-result test-fail";
      result.textContent = "Cannot reach the server. Make sure it's running on this port.";
    }
    btn.disabled = false;
  });
</script>
</div>
</body>
</html>
"""

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
