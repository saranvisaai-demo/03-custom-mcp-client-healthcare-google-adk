# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A minimal Google ADK (Agent Development Kit) agent that connects to a local
custom Healthcare MCP server over Streamable HTTP, exposing its tools
(patient risk, readmission insights, schema introspection, SQL queries) to an
`LlmAgent` running Gemini. The entire agent definition lives in
`mcp_client_google_adk/agent.py`. This repo is the **client** only — it has no
local tool implementations; it expects a compatible Healthcare MCP server
(see the sibling `03-custom-mcp-server-healthcare` project) to already be
running locally.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file (gitignored) in the repo root with:

```
MCP_URL=http://127.0.0.1:8000/mcp
```

`agent.py` loads this via `python-dotenv`; if `MCP_URL` is unset it defaults
to `http://127.0.0.1:8000/mcp`. No API key / auth header is needed — the
local server doesn't require one.

## Running the agent

The Healthcare MCP server must be started first and left running — this
agent has no local tools and every data request depends on that server being
reachable at `MCP_URL`.

This follows the standard ADK project layout (an agent package directory
containing `agent.py` with a module-level `root_agent`), so the ADK CLI can
discover and run it from the repo root:

```bash
adk web                        # launch the ADK dev UI and chat with the agent in a browser
adk run mcp_client_google_adk  # run the agent directly in the terminal
```

There is no custom entrypoint script, test suite, or lint config in this
project — `adk web`/`adk run` and manual inspection are the only ways to
exercise it.

## Architecture notes

- `mcp_client_google_adk/agent.py` wires together three ADK pieces:
  - `StreamableHTTPConnectionParams` — connection config pointing at the
    local Healthcare MCP endpoint (`MCP_URL`). No headers are sent.
  - `McpToolset` — wraps that MCP connection so its tools can be handed to an
    agent.
  - `LlmAgent` — the Gemini-backed agent (`root_agent`) that receives the
    `healthcare_toolset` as its `tools`.
- ADK discovers agents by convention: it looks for a `root_agent` variable in
  an `agent.py` inside a package directory (here, `mcp_client_google_adk/`).
  Keep that name and location if extending this agent, or add sibling package
  directories for additional agents.
- Both the client (this repo) and the server run on `localhost`. Start the
  server before the client; there's no retry/reconnect logic here, so if the
  server isn't up yet, tool calls will fail.
- `.env` is gitignored — never commit it. `MCP_URL` is the only variable it
  currently holds.

## Gotchas / history

- This was originally scaffolded from a Google Maps MCP client example
  (`03-mcp-google-adk`), which authenticates to Google's hosted MCP endpoint
  via an `X-Goog-Api-Key` header. That header and the Maps-specific
  `MAPS_API_KEY` env var do **not** apply here — the local Healthcare MCP
  server needs no auth. If you see either of those reappear (e.g. from
  copy-pasting another agent.py), remove them.
