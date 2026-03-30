from __future__ import annotations
import json
from typing import Any
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from mcp_layer.client import MCPClient
from agent.react import ReActEngine
from config import config
from utils.logger import get_logger
log = get_logger("nodes")
from typing import TypedDict, Annotated
import operator
class AgentState(TypedDict):
    emails: list[dict]
    decisions: list[dict]
    results: list[dict]
    summary: str
PLANNER_PROMPT = """\
You are a personal productivity assistant. Analyse the email below and decide
what action to take.
## Email
From: {sender}
Subject: {subject}
Date: {date}
Body:
{body}
---
Respond in **valid JSON only** with:
{{
  "action": "create_task" | "schedule_event" | "ignore",
  "reason": "why you chose this action",
  "details": {{
    // If create_task: "title", "description", "priority" (high/medium/low), "due_date" (YYYY-MM-DD or null)
    // If schedule_event: "title", "description", "start_datetime" (ISO), "end_datetime" (ISO), "location" (or null)
    // If ignore: empty object {{}}
  }}
}}
Be practical. Only create tasks or events for truly actionable emails.
Newsletters, promotions, and automated notifications should be ignored.
"""
class PlannerNode:
    def __init__(self) -> None:
        self.llm = ChatOllama(
            base_url=config.ollama.base_url,
            model=config.ollama.model,
            temperature=config.ollama.temperature,
        )
    def __call__(self, state: AgentState) -> AgentState:
        emails = state.get("emails", [])
        decisions: list[dict] = []
        for email in emails:
            log.info(f"📧 Analysing: {email.get('subject', '?')}")
            prompt = PLANNER_PROMPT.format(
                sender=email.get("sender", ""),
                subject=email.get("subject", ""),
                date=email.get("date", ""),
                body=email.get("body", email.get("snippet", ""))[:1500],
            )
            response = self.llm.invoke([HumanMessage(content=prompt)])
            parsed = self._parse(response.content)
            parsed["email_id"] = email.get("id", "")
            parsed["email_subject"] = email.get("subject", "")
            action = parsed.get("action", "ignore")
            log.info(f"  → Decision: {action} | {parsed.get('reason', '')[:100]}")
            decisions.append(parsed)
        return {"decisions": decisions}
    @staticmethod
    def _parse(raw: str) -> dict:
        import re
        try:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                return json.loads(match.group())
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"action": "ignore", "reason": f"Failed to parse: {raw[:200]}", "details": {}}
class ExecutorNode:
    def __init__(self, mcp_client: MCPClient) -> None:
        self.react = ReActEngine(mcp_client)
        self.mcp = mcp_client
    def __call__(self, state: AgentState) -> AgentState:
        decisions = state.get("decisions", [])
        results: list[dict] = []
        for decision in decisions:
            action = decision.get("action", "ignore")
            details = decision.get("details", {})
            email_subject = decision.get("email_subject", "?")
            if action == "ignore":
                log.info(f"⏭  Ignoring: {email_subject}")
                results.append({
                    "email_subject": email_subject,
                    "action": "ignore",
                    "success": True,
                    "detail": decision.get("reason", "Not actionable"),
                })
                continue
            if action in ("create_task", "schedule_event"):
                log.info(f"🤖 ReAct Engine taking over to execute {action} for: {email_subject}")
                task_prompt = (
                    f"Email Subject: '{email_subject}'.\n"
                    f"The planner decided the action is: {action}.\n"
                    f"Here are the necessary details to execute: {json.dumps(details)}.\n"
                    f"Please use your tools to complete this action and provide a final answer summary."
                )
                
                react_result = self.react.run(task_prompt)
                
                results.append({
                    "email_subject": email_subject,
                    "action": action,
                    "success": react_result.get("success", False),
                    "detail": react_result.get("final_answer", "No final answer from ReAct agent."),
                })
        return {"results": results}
class SummarizerNode:
    def __call__(self, state: AgentState) -> AgentState:
        results = state.get("results", [])
        lines = ["📊 Productivity Agent — Session Summary", "=" * 45]
        for r in results:
            icon = {"create_task": "📝", "schedule_event": "📅", "ignore": "⏭"}.get(r["action"], "•")
            status = "✓" if r.get("success") else "✗"
            lines.append(f"  {icon} {status} [{r['action']}] {r['email_subject']}")
            if r.get("detail"):
                lines.append(f"      → {str(r['detail'])[:120]}")
        summary = "\n".join(lines)
        log.info(f"\n{summary}")
        return {"summary": summary}
