# 📧 MCP-Based Personal Productivity Agent

An autonomous AI assistant that reads your emails and automatically manages your tasks and calendar using entirely local AI. 

Powered by **local Ollama LLM**, **LangGraph**, and the **Model Context Protocol (MCP)**.

## 🚀 TL;DR: How it works

1. **Reads**: Securely connects to your Gmail and fetches your recent emails.
2. **Thinks**: Uses a local LLM via Ollama + LangGraph to analyze each email and decide if it's actionable (e.g., a task request, a meeting invite) or just noise (e.g., promotional newsletters).
3. **Acts**: Using the Model Context Protocol (MCP), it triggers specific tools to either:
   - Create a task in your **Notion** database.
   - Schedule an event in your **Google Calendar**.
   - Ignore it if no action is needed.

## 🌟 Why it's cool

- **Privacy-First**: It uses a local Ollama model (like `qwen2.5:7b` or `llama3.2`) to process your data, meaning your sensitive email contents aren't being sent to external APIs like OpenAI or Anthropic.
- **Modern Architecture**: It uses the powerful new Model Context Protocol (MCP) standard to seamlessly plug tools into the LLM, making it modular and highly extensible.

## ⚙️ Configuration

Create a `.env` file (or update the provided one) in the root directory:

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_MODEL` | Ollama model to use | `qwen2.5:7b` |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `GMAIL_MAX_EMAILS` | Max emails to fetch | `3` |
| `MAX_REACT_STEPS` | ReAct loop step limit | `8` |
| `NOTION_API_KEY` | Your Notion Integration Token | - |
| `NOTION_TASKS_DB_ID`| Your Notion Tasks Database ID | - |

*(Note: API Credentials for Gmail and Google Calendar should be placed in the `credentials/` folder as `gmail_credentials.json` and `gcal_credentials.json`)*

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Ollama (local, e.g. `qwen2.5:7b`) |
| Agent Framework | LangChain + LangGraph |
| Tool Protocol | Model Context Protocol (MCP) |
| Email | Gmail API (OAuth2) |
| Tasks | Notion API |
| Calendar | Google Calendar API (OAuth2) |
| Models | Pydantic v2 |

## 💻 Quickstart

### Prerequisites:
- Python 3.10+
- [Ollama](https://ollama.com/) installed and running (`ollama serve`).

### Setup
1. Clone the repository.
2. Pull your desired model in Ollama: `ollama pull qwen2.5:7b`
3. Install dependencies: `pip install -r requirements.txt`
4. Set up your `.env` variables and `credentials/` tokens.

### Run

**Full Pipeline Mode:**
Runs the complete autonomous workflow: fetching live emails, planning, and executing the API calls to Notion & Calendar.
```bash
python main.py
```

**Demo Mode:**
Want to test the logic without real API connections? Demo mode uses mock emails and tests the planner's decisions without making actual tool calls.
```bash
python main.py --demo
```
