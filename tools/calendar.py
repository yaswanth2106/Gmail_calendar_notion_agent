from __future__ import annotations
import os
from typing import Any
from mcp_layer.protocol import (
    MCPTool,
    MCPToolSchema,
    MCPParameter,
    MCPParameterType,
    MCPToolResult,
)
from models.event import CalendarEvent
from config import config
class CalendarCreateEventTool(MCPTool):
    def schema(self) -> MCPToolSchema:
        return MCPToolSchema(
            name="calendar_create_event",
            description="Create a new event in Google Calendar with title, start/end time, and optional location.",
            parameters=[
                MCPParameter(name="title", description="Event title/summary."),
                MCPParameter(
                    name="start_datetime",
                    description="Event start in ISO format: YYYY-MM-DDTHH:MM:SS",
                ),
                MCPParameter(
                    name="end_datetime",
                    description="Event end in ISO format: YYYY-MM-DDTHH:MM:SS",
                ),
                MCPParameter(
                    name="description",
                    description="Event description.",
                    required=False,
                    default="",
                ),
                MCPParameter(
                    name="location",
                    description="Event location.",
                    required=False,
                ),
                MCPParameter(
                    name="attendees",
                    description="Comma-separated email addresses of attendees.",
                    required=False,
                    default="",
                ),
            ],
        )
    def execute(self, **kwargs) -> MCPToolResult:
        title = kwargs.get("title", "")
        start = kwargs.get("start_datetime", "")
        end = kwargs.get("end_datetime", "")
        if not title or not start or not end:
            return MCPToolResult(
                success=False,
                error="title, start_datetime, and end_datetime are required.",
            )
        event = CalendarEvent(
            title=title,
            description=kwargs.get("description", ""),
            start_datetime=start,
            end_datetime=end,
            location=kwargs.get("location"),
            attendees=[
                a.strip()
                for a in kwargs.get("attendees", "").split(",")
                if a.strip()
            ],
        )
        try:
            service = self._get_calendar_service()
            body: dict[str, Any] = {
                "summary": event.title,
                "description": event.description,
                "start": {
                    "dateTime": event.start_datetime,
                    "timeZone": "Asia/Kolkata",
                },
                "end": {
                    "dateTime": event.end_datetime,
                    "timeZone": "Asia/Kolkata",
                },
            }
            if event.location:
                body["location"] = event.location
            if event.attendees:
                body["attendees"] = [{"email": e} for e in event.attendees]
            result = (
                service.events()
                .insert(calendarId=config.calendar.calendar_id, body=body)
                .execute()
            )
            return MCPToolResult(
                success=True,
                data={
                    "event_id": result.get("id", ""),
                    "link": result.get("htmlLink", ""),
                    "title": event.title,
                    "start": event.start_datetime,
                },
            )
        except FileNotFoundError:
            return MCPToolResult(
                success=False,
                error=f"Calendar credentials not found at '{config.calendar.credentials_file}'. "
                      f"See README for setup instructions.",
            )
        except Exception as e:
            return MCPToolResult(success=False, error=str(e))
    def _get_calendar_service(self) -> Any:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        creds = None
        token_path = config.calendar.token_file
        creds_path = config.calendar.credentials_file
        if not os.path.exists(creds_path):
            raise FileNotFoundError(creds_path)
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, config.calendar.scopes)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, config.calendar.scopes)
                creds = flow.run_local_server(port=0)
            with open(token_path, "w") as f:
                f.write(creds.to_json())
        return build("calendar", "v3", credentials=creds)
