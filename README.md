# 📧 MCP-Based Personal Productivity Agent

An agentic AI system that reads your emails, decides what to do, and automates task creation (Notion) and event scheduling (Google Calendar) — all powered by **local Ollama LLM** and **Model Context Protocol (MCP)**.


## ⚙️ Configuration

All settings are in `.env:

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
