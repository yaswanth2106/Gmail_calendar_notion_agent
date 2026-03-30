from pydantic import BaseModel
from typing import Optional
class CalendarEvent(BaseModel):
    title: str
    description: str = ""
    start_datetime: str
    end_datetime: str
    location: Optional[str] = None
    attendees: list[str] = []
    source_email_id: Optional[str] = None
