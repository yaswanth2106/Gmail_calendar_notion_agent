# 📧 MCP-Based Personal Productivity Agent

An AI assistant that reads your emails and automatically manages your tasks and calendar using entirely local AI. 

Powered by **local Ollama LLM**, **LangGraph**, and the **Model Context Protocol (MCP)**.

##  TL;DR: How it works

1. **Reads**: Securely connects to your Gmail and fetches your recent emails.
2. **Thinks**: Uses a local LLM via Ollama + LangGraph to analyze each email and decide if it's actionable (e.g., a task request, a meeting invite) or just noise (e.g., promotional newsletters).
3. **Acts**: Using the Model Context Protocol (MCP), it triggers specific tools to either:
   - Create a task in your **Notion** database.
   - Schedule an event in your **Google Calendar**.
   - Ignore it if no action is needed.


- **Privacy-First**: It uses a local Ollama model (like `qwen2.5:7b` or `llama3.2`) to process your data, meaning your sensitive email contents aren't being sent to external APIs like OpenAI or Anthropic.
- **Modern Architecture**: It uses the powerful new Model Context Protocol (MCP) standard to seamlessly plug tools into the LLM, making it modular and highly extensible.




| `OLLAMA_MODEL` | Ollama model to use | `qwen2.5:7b` |
| `GMAIL_MAX_EMAILS` | Max emails to fetch | `3` |
| `MAX_REACT_STEPS` | ReAct loop step limit | `8` |



##  Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Ollama (local, e.g. `qwen2.5:7b`) |
| Agent Framework | LangChain + LangGraph |
| Tool Protocol | Model Context Protocol (MCP) |
| Email | Gmail API (OAuth2) |
| Tasks | Notion API |
| Calendar | Google Calendar API (OAuth2) |
| Models | Pydantic v2 |




