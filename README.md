# 📧 MCP-Based Personal Productivity Agent

An agentic AI system that reads your emails, decides what to do, and automates task creation (Notion) and event scheduling (Google Calendar) — all powered by **local Ollama LLM** and **Model Context Protocol (MCP)**.

## 🏗️ Architecture

```
User → main.py
         │
         ▼
┌──────────────────────────────────────────────────┐
│              LangGraph Workflow                   │
│                                                   │
│  ┌──────────┐   ┌─────────┐   ┌──────────┐      │
│  │  Email    │──▶│ Planner │──▶│ Executor │──┐   │
│  │  Reader   │   │  Node   │   │   Node   │  │   │
│  └──────────┘   └─────────┘   └──────────┘  │   │
│                       │             │         │   │
│                  (LLM decides)  (ReAct loop)  │   │
│                       │             │         ▼   │
│                       ▼             ▼    ┌──────┐│
│                  create_task    MCP Tools │Summa-││
│                  schedule_event          │rizer ││
│                  ignore                  └──────┘│
└──────────────────────────────────────────────────┘
                          │
                          ▼
                ┌─────────────────┐
                │   MCP Layer     │
                │  (Unified API)  │
                └──┬──────┬──────┘
                   │      │      │
                   ▼      ▼      ▼
               Gmail   Notion  Calendar
```

## 📁 Project Structure

```
lang_agent/
├── main.py                  # Entry point (full pipeline + demo mode)
├── config.py                # All configuration via .env
├── requirements.txt
├── .env.example             # Template for API keys
│
├── agent/                   # Agent logic
│   ├── graph.py             # LangGraph workflow definition
│   ├── nodes.py             # Planner, Executor, Summarizer nodes
│   └── react.py             # ReAct reasoning engine
│
├── mcp_layer/               # Model Context Protocol
│   ├── protocol.py          # MCPTool base, MCPToolSchema, MCPToolResult
│   └── client.py            # Tool registry + unified dispatcher
│
├── tools/                   # MCP tool implementations
│   ├── gmail.py             # Read emails (Gmail API + OAuth2)
│   ├── notion.py            # Create tasks (Notion API)
│   └── calendar.py          # Schedule events (Calendar API + OAuth2)
│
├── models/                  # Pydantic data models
│   ├── email.py             # EmailMessage
│   ├── task.py              # TaskItem (with priority/status enums)
│   └── event.py             # CalendarEvent
│
├── utils/
│   └── logger.py            # Logging setup
│
└── credentials/             # OAuth tokens (gitignored)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.ai) running locally with `llama3.2`

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Demo Mode (No API Keys Needed)

```bash
# Make sure Ollama is running
ollama serve

# Run with mock emails to test the planner
python main.py --demo
```

This uses 3 mock emails to show how the agent decides what action to take — without needing any API credentials.

### 3. Full Mode (Requires API Setup)

```bash
# Copy and fill in your API keys
cp .env.example .env

# Run the full pipeline
python main.py
```

## 🔑 API Setup

### Gmail & Google Calendar

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project → Enable **Gmail API** and **Google Calendar API**
3. Create **OAuth 2.0 Client ID** (Desktop app)
4. Download the JSON → save as `credentials/gmail_credentials.json`
5. Copy the same file as `credentials/gcal_credentials.json` (or use a separate one)
6. First run will open a browser for OAuth consent

### Notion

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Create a new integration → copy the **API key**
3. Create a database in Notion with columns:
   - `Name` (title)
   - `Priority` (select: High, Medium, Low)
   - `Due Date` (date)
   - `Tags` (multi-select)
4. Share the database with your integration
5. Copy the **database ID** from the URL
6. Set both in `.env`:
   ```
   NOTION_API_KEY=secret_xxx
   NOTION_TASKS_DB_ID=xxx
   ```

## ⚙️ Configuration

All settings are in `.env` (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_MODEL` | Ollama model to use | `llama3.2` |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `GMAIL_MAX_EMAILS` | Max emails to fetch | `10` |
| `MAX_REACT_STEPS` | ReAct loop step limit | `8` |

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Ollama (local, `llama3.2`) |
| Agent Framework | LangChain + LangGraph |
| Tool Protocol | Model Context Protocol (MCP) |
| Email | Gmail API (OAuth2) |
| Tasks | Notion API |
| Calendar | Google Calendar API (OAuth2) |
| Models | Pydantic v2 |
