# Healthcare MCP Client (Google ADK)

A minimal Google ADK (Agent Development Kit) agent that connects to a local
custom Healthcare MCP server over Streamable HTTP, exposing its healthcare
analytics tools (patient risk, readmission insights, schema, SQL queries) to
an `LlmAgent` running Gemini. The entire agent definition lives in
`mcp_client_google_adk/agent.py`.

- **Entry point:** `mcp_client_google_adk/agent.py` — the whole agent is
  defined here.
- **How it works:** it wraps a `StreamableHTTPConnectionParams` connection to
  a locally-hosted MCP endpoint (default `http://127.0.0.1:8000/mcp`, set via
  `MCP_URL`) in an `McpToolset`, then hands that toolset to an `LlmAgent`
  (`root_agent`) running on Gemini.
- **No local tools:** all healthcare functionality (patient data, diagnoses,
  lab results, visits) lives on the separate Healthcare MCP server — this
  repo only wires up the client side.
- **Run it:** `adk web` (browser chat UI) or `adk run mcp_client_google_adk`
  (terminal), with the Healthcare MCP server already running locally.

This is a client only — it expects the companion
[Healthcare MCP server](../03-custom-mcp-server-healthcare) (or any
compatible server) to already be running at the configured `MCP_URL` before
the agent can retrieve any data.

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

`agent.py` loads this via `python-dotenv`; if unset, it falls back to
`http://127.0.0.1:8000/mcp`.

## Running the agent

1. Start the Healthcare MCP server first (in the sibling project), e.g.:

   ```bash
   python server.py   # from 03-custom-mcp-server-healthcare
   ```

   It should log something like
   `Starting Healthcare MCP Server on http://0.0.0.0:8000/mcp`.

2. Then, from this project, launch the ADK agent. This follows the standard
   ADK project layout (an agent package directory containing `agent.py` with
   a module-level `root_agent`), so the ADK CLI can discover and run it from
   the repo root:

   ```bash
   adk web                        # launch the ADK dev UI and chat with the agent in a browser
   adk run mcp_client_google_adk  # run the agent directly in the terminal
   ```

There is no custom entrypoint script, test suite, or lint config in this
project — `adk web`/`adk run` and manual inspection are the only ways to
exercise it.

## Architecture notes

```
 User                LlmAgent                  McpToolset               Healthcare
 input      ────▶   (Gemini)          ────▶   (MCP client,     ────▶   MCP server
 "summarize            │                        Streamable HTTP)        (local,
  risk for               │                         │                     http://127.0.0.1:8000)
  patient 7"             │  decides it needs       │                         │
                         │  a healthcare tool,      │                         │
                         │  calls it    ────────────▶                         │
                         │                          │  forwards call ─────────▶
                         │                          │                         │
                         │                          │  ◀──── tool result ─────┘
                         │  ◀── tool result ─────────┘      (JSON)
                         │
 reply     ◀───── natural-language answer
 to user           grounded in the tool result
```

- `mcp_client_google_adk/agent.py` wires together three ADK pieces:
  - `StreamableHTTPConnectionParams` — connection config pointing at the
    local Healthcare MCP endpoint (`MCP_URL`, default
    `http://127.0.0.1:8000/mcp`). No auth headers are sent — the local
    server doesn't require any.
  - `McpToolset` — wraps that MCP connection so its tools can be handed to an
    agent.
  - `LlmAgent` — the Gemini-backed agent (`root_agent`) that receives the
    `healthcare_toolset` as its `tools`.
- ADK discovers agents by convention: it looks for a `root_agent` variable in
  an `agent.py` inside a package directory (here, `mcp_client_google_adk/`).
  Keep that name and location if extending this agent.
- All healthcare functionality comes from the remote (but locally-hosted) MCP
  server — there is no local tool implementation to maintain in this repo;
  changes to tool behavior happen in the server project, not here.
- Server and client both run on `localhost`/`127.0.0.1`, so the server must be
  started first and kept running for the agent's tool calls to succeed.
