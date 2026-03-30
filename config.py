import os
from dataclasses import dataclass, field
from dotenv import load_dotenv
load_dotenv()
@dataclass
class OllamaConfig:
    base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    temperature: float = float(os.getenv("OLLAMA_TEMPERATURE", "0.3"))
@dataclass
class GmailConfig:
    credentials_file: str = os.getenv("GMAIL_CREDENTIALS_FILE", "credentials/gmail_credentials.json")
    token_file: str = os.getenv("GMAIL_TOKEN_FILE", "credentials/gmail_token.json")
    scopes: list[str] = field(default_factory=lambda: [
        "https://www.googleapis.com/auth/gmail.readonly",
    ])
    max_emails: int = int(os.getenv("GMAIL_MAX_EMAILS", "10"))
@dataclass
class NotionConfig:
    api_key: str = os.getenv("NOTION_API_KEY", "")
    tasks_database_id: str = os.getenv("NOTION_TASKS_DB_ID", "")
@dataclass
class CalendarConfig:
    credentials_file: str = os.getenv("GCAL_CREDENTIALS_FILE", "credentials/gcal_credentials.json")
    token_file: str = os.getenv("GCAL_TOKEN_FILE", "credentials/gcal_token.json")
    scopes: list[str] = field(default_factory=lambda: [
        "https://www.googleapis.com/auth/calendar",
    ])
    calendar_id: str = os.getenv("GCAL_CALENDAR_ID", "primary")
@dataclass
class AppConfig:
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    gmail: GmailConfig = field(default_factory=GmailConfig)
    notion: NotionConfig = field(default_factory=NotionConfig)
    calendar: CalendarConfig = field(default_factory=CalendarConfig)
    verbose: bool = os.getenv("VERBOSE", "true").lower() == "true"
    max_react_steps: int = int(os.getenv("MAX_REACT_STEPS", "8"))
config = AppConfig()
