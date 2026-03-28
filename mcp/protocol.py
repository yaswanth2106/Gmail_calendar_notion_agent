"""
MCP Protocol types.

Defines the standardised interface that all tools expose.
This mirrors the Model Context Protocol schema so tools
are discoverable and callable through a uniform contract.
"""

from pydantic import BaseModel, Field
from typing import Any, Optional
from enum import Enum


class MCPParameterType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"


class MCPParameter(BaseModel):
    """A single parameter in an MCP tool schema."""
    name: str
    description: str
    type: MCPParameterType = MCPParameterType.STRING
    required: bool = True
    default: Optional[Any] = None


class MCPToolSchema(BaseModel):
    """Full schema describing an MCP tool."""
    name: str
    description: str
    parameters: list[MCPParameter] = Field(default_factory=list)


class MCPToolResult(BaseModel):
    """Standardised result from an MCP tool call."""
    success: bool
    data: Any = None
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.success:
            return str(self.data)
        return f"ERROR: {self.error}"


class MCPTool:
    """
    Base class for MCP-compatible tools.

    Every tool (Gmail, Notion, Calendar) extends this and implements:
      - schema() → MCPToolSchema
      - execute(**kwargs) → MCPToolResult
    """

    def schema(self) -> MCPToolSchema:
        raise NotImplementedError

    def execute(self, **kwargs) -> MCPToolResult:
        raise NotImplementedError

    def safe_execute(self, **kwargs) -> MCPToolResult:
        """Wrapper with error catching."""
        try:
            return self.execute(**kwargs)
        except Exception as exc:
            return MCPToolResult(success=False, data=None, error=str(exc))

    @property
    def name(self) -> str:
        return self.schema().name

    @property
    def description(self) -> str:
        return self.schema().description
