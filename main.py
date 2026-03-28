"""
MCP-Based Personal Productivity Agent
======================================

Entry point. Wires MCP tools + LangGraph workflow and runs the agent.

Usage:
  python main.py              # Full pipeline: read emails → plan → execute → summarize
  python main.py --demo       # Demo mode with mock emails (no API keys needed)
"""

import sys

from config import config
from mcp_layer.client import MCPClient
from tools import ALL_TOOLS
from agent.graph import build_agent_graph
from utils.logger import get_logger

log = get_logger("main")


# ── Mock data for demo mode ─────────────────────────

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
    """Run the complete agent pipeline: Gmail → Planner → Executor → Summary."""
    log.info("🚀 Starting MCP Personal Productivity Agent")
    log.info(f"   LLM: Ollama ({config.ollama.model}) @ {config.ollama.base_url}")

    # Register MCP tools
    mcp = MCPClient()
    mcp.register_many(ALL_TOOLS)
    log.info(f"   🔧 MCP Tools: {mcp.list_tools()}")

    # Build LangGraph workflow
    graph = build_agent_graph(mcp)

    # Run the graph
    initial_state = {
        "emails": [],
        "decisions": [],
        "results": [],
        "summary": "",
    }

    final_state = graph.invoke(initial_state)
    print(f"\n{final_state.get('summary', '(no summary)')}")


def run_demo_mode() -> None:
    """
    Demo mode — uses mock emails instead of real Gmail API.
    No API keys needed. Shows the planner deciding actions.
    """
    log.info("🎭 Starting in DEMO MODE (mock emails, no API calls)")
    log.info(f"   LLM: Ollama ({config.ollama.model}) @ {config.ollama.base_url}")

    # Import nodes directly for demo
    from agent.nodes import PlannerNode, SummarizerNode, AgentState

    planner = PlannerNode()

    state: AgentState = AgentState({
        "emails": MOCK_EMAILS,
        "decisions": [],
        "results": [],
        "summary": "",
    })

    # Step 1: Plan
    log.info(f"\n📩 Loaded {len(MOCK_EMAILS)} mock email(s)")
    state = planner(state)

    # Step 2: Show decisions (skip real execution in demo)
    print("\n" + "=" * 55)
    print("  📊 Demo Results — Planner Decisions")
    print("=" * 55)

    for d in state.get("decisions", []):
        action = d.get("action", "?")
        icon = {"create_task": "📝", "schedule_event": "📅", "ignore": "⏭"}.get(action, "•")
        print(f"\n  {icon} {d.get('email_subject', '?')}")
        print(f"     Action: {action}")
        print(f"     Reason: {d.get('reason', 'N/A')[:150]}")
        details = d.get("details", {})
        if details:
            for k, v in details.items():
                print(f"     {k}: {v}")

    # Step 3: Summary
    state["results"] = [
        {
            "email_subject": d.get("email_subject", "?"),
            "action": d.get("action", "ignore"),
            "success": True,
            "detail": f"(demo) {d.get('reason', '')[:100]}",
        }
        for d in state.get("decisions", [])
    ]

    summarizer = SummarizerNode()
    state = summarizer(state)


def main() -> None:
    if "--demo" in sys.argv:
        run_demo_mode()
    else:
        run_full_pipeline()


if __name__ == "__main__":
    main()
