"""
ReAct Engine — Reason + Act loop powered by Ollama.

The engine receives:
  - A task description (from the planner)
  - Available MCP tools (from the client)
  - And iterates: Thought → Action → Observation → ... → Final Answer
"""

from __future__ import annotations

import json
import re
from typing import Any

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

from mcp_layer.client import MCPClient
from config import config
from utils.logger import get_logger

log = get_logger("react")


# ── Prompt Templates ────────────────────────────────

REACT_SYSTEM = """\
You are a personal productivity AI agent. You process emails and take actions
(create tasks, schedule events, or ignore) using the tools available to you.

## Available Tools
{tools}

## Instructions
For each step, respond in **valid JSON only** with ONE of:

1. To use a tool:
{{"thought": "your reasoning", "action": "tool_name", "arguments": {{...}}}}

2. To give the final answer (when you're done):
{{"thought": "your reasoning", "final_answer": "summary of what you did"}}

Rules:
- Think step by step.
- Use tools only when needed.
- After observing a tool result, decide your next action.
- Respond with JSON only. No markdown, no extra text.
"""

REACT_USER = """\
## Task
{task}

## Execution History
{history}

What is your next step? Respond in JSON only.
"""


class ReActEngine:
    """
    ReAct loop that uses Ollama (via LangChain ChatOllama)
    and MCP tools to complete a task.
    """

    def __init__(self, mcp_client: MCPClient) -> None:
        self.mcp = mcp_client
        self.llm = ChatOllama(
            base_url=config.ollama.base_url,
            model=config.ollama.model,
            temperature=config.ollama.temperature,
        )
        self.max_steps = config.max_react_steps

    def run(self, task: str) -> dict[str, Any]:
        """
        Execute the ReAct loop for a given task.

        Returns:
            {
                "final_answer": str,
                "steps": [ {thought, action, arguments, observation}, ... ],
                "success": bool,
            }
        """
        system_prompt = REACT_SYSTEM.format(tools=self.mcp.describe_for_llm())
        history_lines: list[str] = []
        steps: list[dict] = []

        for step_num in range(1, self.max_steps + 1):
            log.info(f"Step {step_num}/{self.max_steps}")

            user_prompt = REACT_USER.format(
                task=task,
                history="\n".join(history_lines) if history_lines else "(none yet)",
            )

            # Call LLM
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ])
            raw = response.content
            parsed = self._parse_response(raw)

            thought = parsed.get("thought", "")
            if thought:
                log.info(f"  💭 {thought}")

            # ── Final answer? ──
            if "final_answer" in parsed:
                log.info(f"  ✅ Final: {parsed['final_answer'][:200]}")
                return {
                    "final_answer": parsed["final_answer"],
                    "steps": steps,
                    "success": True,
                }

            # ── Tool action ──
            action = parsed.get("action", "")
            arguments = parsed.get("arguments", {})

            if action:
                log.info(f"  ⚙  Action: {action}({json.dumps(arguments)})")
                result = self.mcp.call(action, **arguments)
                observation = str(result)
                log.info(f"  {'✓' if result.success else '✗'} Observation: {observation[:300]}")

                steps.append({
                    "step": step_num,
                    "thought": thought,
                    "action": action,
                    "arguments": arguments,
                    "observation": observation,
                    "success": result.success,
                })

                history_lines.append(
                    f"Step {step_num}:\n"
                    f"  Thought: {thought}\n"
                    f"  Action: {action}({json.dumps(arguments)})\n"
                    f"  Observation: {observation[:500]}"
                )
            else:
                history_lines.append(
                    f"Step {step_num}: (no valid action — please use a tool or give final_answer)"
                )

        # Exhausted steps
        return {
            "final_answer": "(Agent reached step limit without final answer)",
            "steps": steps,
            "success": False,
        }

    @staticmethod
    def _parse_response(raw: str) -> dict:
        """Extract JSON from LLM response."""
        try:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                return json.loads(match.group())
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"thought": raw[:300], "final_answer": raw}
