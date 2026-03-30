from pydantic import BaseModel, Field
from typing import Optional
class EmailMessage(BaseModel):
    id: str = ""
    subject: str = ""
    sender: str = ""
    to: str = ""
    date: str = ""
    snippet: str = ""
    body: str = ""
    labels: list[str] = Field(default_factory=list)
    @property
    def summary(self) -> str:
        return f"From: {self.sender} | Subject: {self.subject} | Date: {self.date}"
