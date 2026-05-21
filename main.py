import sys
from config import config
from mcp_layer.client import MCPClient
from tools import ALL_TOOLS
from agent.graph import build_agent_graph
from utils.logger import get_logger
log = get_logger("main")
MOCK_EMAILS = [
    {
        "id": "demo_001",
        "subject": "Team standup moved to 3 PM tomorrow",
        "sender": "manager@company.com",
        "date": "2026-03-28",
        "snippet": "Hi team, the daily standup is rescheduled to 3 PM tomorrow.",
        "body": "Hi team,\n\nThe daily standup has been moved to 3:00 PM tomorrow (March 29). "
                "Please update your calendars.\n\nThanks,\nManager",
    },
    {
        "id": "demo_002",
        "subject": "Action Required: Review PR #142 by Friday",
        "sender": "lead@company.com",
        "date": "2026-03-28",
        "snippet": "Please review the pull request for the auth module.",
        "body": "Hi,\n\nPlease review PR #142 (auth module refactor) by end of day Friday. "
                "It's blocking the release.\n\nPriority: High\n\nThanks",
    },
    {
        "id": "demo_003",
        "subject": "Your weekly newsletter from TechDigest",
        "sender": "newsletter@techdigest.com",
        "date": "2026-03-28",
        "snippet": "This week in tech: AI breakthroughs, new framework releases...",
        "body": "Top stories this week:\n1. AI breakthroughs\n2. New framework releases\n"
                "3. Industry trends\n\nUnsubscribe | View in browser",
    },
]
def run_full_pipeline() -> None:
    log.info("🚀 Starting MCP Personal Productivity Agent")
    log.info(f"   LLM: Ollama ({config.ollama.model}) @ {config.ollama.base_url}")
    mcp = MCPClient()
    mcp.register_many(ALL_TOOLS)
    log.info(f"   🔧 MCP Tools: {mcp.list_tools()}")
    graph = build_agent_graph(mcp)
    initial_state = {
        "emails": [],
        "decisions": [],
        "results": [],
        "summary": "",
    }
    final_state = graph.invoke(initial_state)
    print(f"\n{final_state.get('summary', '(no summary)')}")
def main() -> None:
    if "--demo" in sys.argv:
        pass
    else:
        run_full_pipeline()
if __name__ == "__main__":
    main()
