from tools.gmail import GmailReadTool
from tools.notion import NotionCreateTaskTool
from tools.calendar import CalendarCreateEventTool
ALL_TOOLS = [
    GmailReadTool(),
    NotionCreateTaskTool(),
    CalendarCreateEventTool(),
]
__all__ = ["ALL_TOOLS", "GmailReadTool", "NotionCreateTaskTool", "CalendarCreateEventTool"]
