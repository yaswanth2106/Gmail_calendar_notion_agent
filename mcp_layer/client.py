"""
MCP Client — registry and dispatcher for all MCP tools.

The agent interacts with tools ONLY through this client,
ensuring a unified interface regardless of the backend (Gmail, Notion, etc.).
"""

from __future__ import annotations

from mcp_layer.protocol import MCPTool, MCPToolSchema, MCPToolResult


class MCPClient:
    """Unified client for discovering and calling MCP tools."""

    def __init__(self) -> None:
        self._tools: dict[str, MCPTool] = {}

    # ── Registration ─────────────────────────────────

    def register(self, tool: MCPTool) -> None:
        schema = tool.schema()
        if schema.name in self._tools:
            raise ValueError(f"Tool '{schema.name}' already registered.")
        self._tools[schema.name] = tool

    def register_many(self, tools: list[MCPTool]) -> None:
        for t in tools:
            self.register(t)

    # ── Discovery ────────────────────────────────────

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())

    def get_schemas(self) -> list[MCPToolSchema]:
        return [t.schema() for t in self._tools.values()]

    def describe_for_llm(self) -> str:
        """
        Generate a human-readable tool catalog for injection
        into the LLM system prompt.
        """
        lines: list[str] = []
        for tool in self._tools.values():
            s = tool.schema()
            params = ", ".join(
                f"{p.name} ({p.type.value}, {'required' if p.required else 'optional'}): {p.description}"
                for p in s.parameters
            )
            lines.append(f"• {s.name}: {s.description}")
            if params:
                lines.append(f"  Parameters: {params}")
        return "\n".join(lines)

    # ── Execution ────────────────────────────────────

    def call(self, tool_name: str, **kwargs) -> MCPToolResult:
        """Call a tool by name through the MCP interface."""
        tool = self._tools.get(tool_name)
        if tool is None:
            return MCPToolResult(
                success=False,
                error=f"Unknown tool: '{tool_name}'. Available: {self.list_tools()}",
            )
        return tool.safe_execute(**kwargs)

    def __len__(self) -> int:
        return len(self._tools)
