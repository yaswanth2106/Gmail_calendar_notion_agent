"""Calendar event data model."""

from pydantic import BaseModel
from typing import Optional


class CalendarEvent(BaseModel):
    """An event to be created in Google Calendar."""
    title: str
    description: str = ""
    start_datetime: str  # ISO format: YYYY-MM-DDTHH:MM:SS
    end_datetime: str    # ISO format: YYYY-MM-DDTHH:MM:SS
    location: Optional[str] = None
    attendees: list[str] = []
    source_email_id: Optional[str] = None
