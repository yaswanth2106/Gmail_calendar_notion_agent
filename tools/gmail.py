"""
Gmail MCP Tool — reads recent emails from Gmail.

Requires OAuth2 credentials:
  1. Create a Google Cloud project
  2. Enable the Gmail API
  3. Download OAuth credentials → credentials/gmail_credentials.json
  4. First run triggers browser-based auth flow → saves token
"""

from __future__ import annotations

import base64
import os
from typing import Any

from mcp_layer.protocol import (
    MCPTool,
    MCPToolSchema,
    MCPParameter,
    MCPParameterType,
    MCPToolResult,
)
from models.email import EmailMessage
from config import config


class GmailReadTool(MCPTool):
    """Read recent emails from Gmail inbox."""

    def schema(self) -> MCPToolSchema:
        return MCPToolSchema(
            name="gmail_read_emails",
            description="Fetch recent emails from Gmail inbox. Returns subject, sender, date, and body snippet.",
            parameters=[
                MCPParameter(
                    name="max_results",
                    description="Maximum number of emails to fetch.",
                    type=MCPParameterType.INTEGER,
                    required=False,
                    default=10,
                ),
                MCPParameter(
                    name="query",
                    description="Gmail search query (e.g. 'is:unread', 'from:boss@company.com').",
                    type=MCPParameterType.STRING,
                    required=False,
                    default="is:unread",
                ),
            ],
        )

    def execute(self, **kwargs) -> MCPToolResult:
        max_results = int(kwargs.get("max_results", config.gmail.max_emails))
        query = kwargs.get("query", "is:unread")

        try:
            service = self._get_gmail_service()
            results = (
                service.users()
                .messages()
                .list(userId="me", q=query, maxResults=max_results)
                .execute()
            )
            messages = results.get("messages", [])

            if not messages:
                return MCPToolResult(success=True, data="No emails found matching the query.")

            emails: list[dict] = []
            for msg_ref in messages:
                msg = (
                    service.users()
                    .messages()
                    .get(userId="me", id=msg_ref["id"], format="full")
                    .execute()
                )
                email = self._parse_message(msg)
                emails.append(email.model_dump())

            return MCPToolResult(success=True, data=emails)

        except FileNotFoundError:
            return MCPToolResult(
                success=False,
                error=f"Gmail credentials not found at '{config.gmail.credentials_file}'. "
                      f"See README for setup instructions.",
            )
        except Exception as e:
            return MCPToolResult(success=False, error=str(e))

    # ── Internal helpers ─────────────────────────────

    def _get_gmail_service(self) -> Any:
        """Build and return an authenticated Gmail API service."""
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build

        creds = None
        token_path = config.gmail.token_file
        creds_path = config.gmail.credentials_file

        if not os.path.exists(creds_path):
            raise FileNotFoundError(creds_path)

        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, config.gmail.scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, config.gmail.scopes)
                creds = flow.run_local_server(port=0)
            with open(token_path, "w") as f:
                f.write(creds.to_json())

        return build("gmail", "v1", credentials=creds)

    @staticmethod
    def _parse_message(msg: dict) -> EmailMessage:
        """Parse a raw Gmail API message into our EmailMessage model."""
        headers = {h["name"].lower(): h["value"] for h in msg.get("payload", {}).get("headers", [])}

        # Extract body
        body = ""
        payload = msg.get("payload", {})
        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain":
                    data = part.get("body", {}).get("data", "")
                    body = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
                    break
        elif "body" in payload:
            data = payload["body"].get("data", "")
            if data:
                body = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

        return EmailMessage(
            id=msg.get("id", ""),
            subject=headers.get("subject", "(no subject)"),
            sender=headers.get("from", ""),
            to=headers.get("to", ""),
            date=headers.get("date", ""),
            snippet=msg.get("snippet", ""),
            body=body[:2000],  # Cap body length
            labels=msg.get("labelIds", []),
        )
