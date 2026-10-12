import os
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

load_dotenv()

MCP_URL = os.getenv("MCP_URL", "http://127.0.0.1:8000/mcp")

healthcare_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=MCP_URL,
    )
)

root_agent = LlmAgent(
    model="gemini-3.1-flash-lite",
    name="mcp_custom_agent_healthcare",
    instruction="You are a helpful assistant that can answer questions about Health care data. You have access to the Healthcare MCP toolset, which allows you to retrieve information about Patients,diagnoses,lab_results, visits and other related data.",
    tools=[healthcare_toolset]
)

