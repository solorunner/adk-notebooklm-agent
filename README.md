# ADK NotebookLM Agent

A Google ADK (Agent Development Kit) agent that wraps the [NotebookLM CLI](https://github.com/solorunner/notebooklm-cli) to orchestrate smart research workflows — creating notebooks, adding sources, querying knowledge, generating studio artifacts, and more.

## Architecture

```
Browser ──► server.py (:8001)
              ├── ADK Agent (Gemini 2.5 Flash)
              │     ├── auth_guard (before every tool call)
              │     └── tools/
              │           ├── auth.py        — check_auth, start_auth, import_cookies
              │           ├── notebooks.py   — create, list, query, delete
              │           ├── sources.py     — add URL/file/text sources
              │           ├── notes.py       — create, list, update, delete notes
              │           ├── research.py    — start, status, import web research
              │           ├── studio.py      — mind maps, slides, infographics, audio, video
              │           ├── download.py    — download generated artifacts
              │           └── sharing.py     — public/private links, invite collaborators
              ├── /auth/* endpoints (Chrome extension cookie flow)
              └── auth_store.py (shared in-memory token store)

Chrome Extension (_extension/)
  └── Captures NotebookLM cookies → POST /auth/cookies
```

## Prerequisites

- **Python 3.11+**
- **[NotebookLM CLI](https://github.com/solorunner/notebooklm-cli)** (`nlm`) installed and on your PATH
- **Google API key** for Gemini (get one at [AI Studio](https://aistudio.google.com/apikey))
- **Google Chrome** (for the auth extension)

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/solorunner/adk-notebooklm-agent.git
cd adk-notebooklm-agent

# 2. Install dependencies
uv sync

# 3. Configure your API key
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# 4. Start the server
uv run python server.py
```

The agent UI will be available at **http://localhost:8001**.

## Chrome Extension Setup

The agent authenticates with NotebookLM via a Chrome extension that forwards your session cookies.

1. Open **http://localhost:8001/auth/install** in Chrome
2. Download and unzip the extension
3. Go to `chrome://extensions`, enable **Developer mode**
4. Click **Load unpacked** and select the `notebooklm-auth-helper` folder
5. When the agent asks you to authenticate, click the extension icon, paste the token, and click **Authenticate**

## Workflows

The agent automatically chains tools into complete workflows when it recognizes your intent:

| # | Workflow | Trigger Example |
|---|----------|----------------|
| 1 | **Topic Research** | "research kubernetes security" |
| 2 | **Project Brain** | "index my codebase at /path/to/src" |
| 3 | **Quick Research** | "find resources about WebAssembly" |
| 4 | **Documentation Hub** | "centralize docs for my project" |
| 5 | **Debugging KB** | "debug KB for Next.js" |
| 6 | **Visualization Suite** | "visualize my notebook" |
| 7 | **Study Pack** | "help me study distributed systems" |
| 8 | **Batch Source Add** | (paste multiple URLs) |
| 9 | **Share & Collaborate** | "share my notebook with team@example.com" |

## Why CLI Instead of MCP?

This agent wraps the `nlm` CLI rather than using an MCP (Model Context Protocol) server. Here's why:

| | CLI (`nlm`) | MCP Server |
|---|---|---|
| **Token cost** | Agent sends a short shell command, gets back a small JSON result. Minimal tokens per tool call. | Every MCP call includes protocol framing, capability negotiation, and verbose structured responses — easily 2-5x more tokens for the same operation. |
| **Latency** | Direct subprocess call — one process spawn, one result. | Requires a persistent MCP server connection with JSON-RPC overhead on every round-trip. |
| **Dependencies** | Zero extra infrastructure. The `nlm` binary is already on `$PATH`. | Needs an MCP server process running alongside the agent, plus SDK dependencies and connection management. |
| **Reliability** | If a CLI call fails, the error is a simple string. Easy to parse, retry, or surface to the user. | MCP connection drops, protocol version mismatches, and serialization errors add failure modes the agent has to handle. |
| **Portability** | Works anywhere Python + `nlm` are installed. No server coordination needed. | Tied to MCP-compatible hosts (Claude Desktop, Cursor, etc.). Doesn't work in plain ADK without custom glue. |
| **Auth model** | CLI uses profile-based cookies managed by `nlm login`. One auth flow, shared across all tools. | MCP servers typically need their own auth configuration, often duplicating what the CLI already handles. |

**Bottom line:** The CLI approach gives the agent the same capabilities with fewer tokens, less infrastructure, and simpler error handling. MCP is great for general-purpose tool discovery, but when you're wrapping a single well-known CLI, the direct approach wins.

## Project Structure

```
├── _extension/              # Chrome auth helper extension
│   ├── manifest.json
│   ├── popup.html / popup.js
│   ├── content.js
│   └── icon48.png
├── notebooklm_agent/        # ADK agent package
│   ├── __init__.py
│   ├── agent.py             # Agent instructions, auth guard, callbacks
│   ├── helpers.py           # CLI wrapper utilities
│   └── tools/               # Tool modules (8 files)
├── auth_store.py            # Shared in-memory auth token store
├── server.py                # FastAPI server (port 8001)
├── pyproject.toml           # Project metadata & dependencies
├── .env.example             # Template for environment variables
├── LICENSE                  # Apache 2.0
└── README.md
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes
4. Push to the branch and open a PR

## License

This project is licensed under the [Apache License 2.0](LICENSE).
