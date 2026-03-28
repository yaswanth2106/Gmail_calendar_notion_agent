"""
LangGraph Workflow — wires the nodes into a stateful graph.

Flow:
  read_emails → planner → executor → summarizer → END
"""

from __future__ import annotations

from langgraph.graph import StateGraph, END

from mcp_layer.client import MCPClient
from agent.nodes import AgentState, PlannerNode, ExecutorNode, SummarizerNode
from utils.logger import get_logger
from config import config

log = get_logger("graph")


def _email_reader_node(mcp_client: MCPClient):
    """Factory: returns a node function that reads emails."""

    def read_emails(state: AgentState) -> AgentState:
        result = mcp_client.call("gmail_read_emails", query="is:unread", max_results=config.gmail.max_emails)

        if result.success and isinstance(result.data, list):
            log.info(f"  Found {len(result.data)} email(s)")
            return {"emails": result.data}
        elif result.success and isinstance(result.data, str):
            log.info(f"  {result.data}")
            return {"emails": []}
        else:
            log.warning(f"  Failed to read emails: {result.error}")
            return {"emails": []}

    return read_emails


def build_agent_graph(mcp_client: MCPClient) -> StateGraph:
    """
    Build and compile the LangGraph workflow.

    Returns a compiled graph that can be invoked with:
        graph.invoke({"emails": [], "decisions": [], "results": [], "summary": ""})
    """
    planner = PlannerNode()
    executor = ExecutorNode(mcp_client)
    summarizer = SummarizerNode()

    # Build the graph
    workflow = StateGraph(AgentState)

    workflow.add_node("read_emails", _email_reader_node(mcp_client))
    workflow.add_node("planner", planner)
    workflow.add_node("executor", executor)
    workflow.add_node("summarizer", summarizer)

    # Define edges: linear pipeline
    workflow.set_entry_point("read_emails")
    workflow.add_edge("read_emails", "planner")
    workflow.add_edge("planner", "executor")
    workflow.add_edge("executor", "summarizer")
    workflow.add_edge("summarizer", END)

    return workflow.compile()
