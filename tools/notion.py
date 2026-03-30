from __future__ import annotations
from mcp_layer.protocol import (
    MCPTool,
    MCPToolSchema,
    MCPParameter,
    MCPParameterType,
    MCPToolResult,
)
from models.task import TaskItem
from config import config
class NotionCreateTaskTool(MCPTool):
    def schema(self) -> MCPToolSchema:
        return MCPToolSchema(
            name="notion_create_task",
            description="Create a new task in the Notion tasks database with title, description, priority, and optional due date.",
            parameters=[
                MCPParameter(name="title", description="Task title."),
                MCPParameter(
                    name="description",
                    description="Task description / details.",
                    required=False,
                    default="",
                ),
                MCPParameter(
                    name="priority",
                    description="Priority level: high, medium, or low.",
                    required=False,
                    default="medium",
                ),
                MCPParameter(
                    name="due_date",
                    description="Due date in YYYY-MM-DD format.",
                    required=False,
                ),
                MCPParameter(
                    name="tags",
                    description="Comma-separated tags for the task.",
                    required=False,
                    default="",
                ),
            ],
        )
    def execute(self, **kwargs) -> MCPToolResult:
        if not config.notion.api_key or not config.notion.tasks_database_id:
            return MCPToolResult(
                success=False,
                error="Notion API key or database ID not configured. Set NOTION_API_KEY and NOTION_TASKS_DB_ID in .env",
            )
        title = kwargs.get("title", "")
        if not title:
            return MCPToolResult(success=False, error="Task title is required.")
        task = TaskItem(
            title=title,
            description=kwargs.get("description", ""),
            priority=kwargs.get("priority", "medium"),
            due_date=kwargs.get("due_date"),
            tags=[t.strip() for t in kwargs.get("tags", "").split(",") if t.strip()],
        )
        try:
            from notion_client import Client as NotionClient
            notion = NotionClient(auth=config.notion.api_key)
            db_info = notion.databases.retrieve(database_id=config.notion.tasks_database_id)
            db_props = db_info.get("properties", {})
            title_prop = next((k for k, v in db_props.items() if v.get("type") == "title"), "Name")
            properties: dict = {
                title_prop: {"title": [{"text": {"content": task.title}}]},
            }
            children = []
            if task.description:
                children.append(
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"text": {"content": task.description}}]
                        },
                    }
                )
            if "Priority" in db_props and db_props["Priority"].get("type") == "select":
                properties["Priority"] = {"select": {"name": task.priority.value.capitalize()}}
            if "Due Date" in db_props and db_props["Due Date"].get("type") == "date" and task.due_date:
                properties["Due Date"] = {"date": {"start": task.due_date}}
            if "Tags" in db_props and db_props["Tags"].get("type") == "multi_select" and task.tags:
                properties["Tags"] = {
                    "multi_select": [{"name": tag} for tag in task.tags]
                }
            result = notion.pages.create(
                parent={"database_id": config.notion.tasks_database_id},
                properties=properties,
                children=children,
            )
            return MCPToolResult(
                success=True,
                data={
                    "page_id": result["id"],
                    "url": result.get("url", ""),
                    "title": task.title,
                },
            )
        except Exception as e:
            return MCPToolResult(success=False, error=str(e))
