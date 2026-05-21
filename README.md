#  MCP-Based Personal Productivity Agent

An AI assistant that reads your emails and automatically manages your tasks and calendar using entirely local AI. 

Powered by **local Ollama LLM**, **LangGraph**, and the **Model Context Protocol (MCP)**.

##  TL;DR: How it works

1. **Reads**: Securely connects to your Gmail and fetches your recent emails.
2. **Thinks**: Uses a local LLM via Ollama + LangGraph to analyze each email and decide if it's actionable (e.g., a task request, a meeting invite) or just noise (e.g., promotional newsletters).
3. **Acts**: Using the Model Context Protocol (MCP), it triggers specific tools to either:
   - Create a task in your **Notion** database.
   - Schedule an event in your **Google Calendar**.
   - Ignore it if no action is needed.

### Workflow Architecture

```mermaid
graph TD
    %% Styling and colors
    classDef startEnd fill:#f1f5f9,stroke:#64748b,stroke-width:2px,color:#0f172a
    classDef mcp fill:#fff7ed,stroke:#f97316,stroke-width:2px,color:#7c2d12
    classDef lgraph fill:#eff6ff,stroke:#3b82f6,stroke-width:2px,color:#1e3a8a
    classDef process fill:#faf5ff,stroke:#a855f7,stroke-width:2px,color:#581c87
    classDef decision fill:#fef08a,stroke:#eab308,stroke-width:2px,color:#713f12

    Start([Start Pipeline]) --> InitMCP[Initialize MCPClient<br/>& Register Tools]
    InitMCP --> CompileGraph[Compile StateGraph]
    CompileGraph --> NodeRead[Node 1: read_emails<br/>Calls MCP 'gmail_read_emails']
    
    subgraph LangGraph Orchestrator
        NodeRead --> NodePlan[Node 2: planner<br/>Ollama analyzes each email]
        NodePlan --> NodeExec[Node 3: executor<br/>Handles actions sequentially]
        NodeExec --> NodeSumm[Node 4: summarizer<br/>Creates status report]
    end

    subgraph Executor Processing Logic
        NodeExec --> ForEach{For Each Email Decision}
        ForEach -->|ignore| LogIgnore[Log skip & record Ignore result]
        ForEach -->|create_task / schedule_event| InitReAct[Initialize ReActEngine]
        
        subgraph ReAct Execution Loop (Max 8 Steps)
            InitReAct --> PromptLLM[Prompt LLM with history & tools]
            PromptLLM --> CheckResponse{Response Type?}
            CheckResponse -->|Action: Call Tool| CallMCP[Call MCP Tool via client]
            CallMCP --> FeedHistory[Record tool observation in history]
            FeedHistory --> PromptLLM
            CheckResponse -->|final_answer| ReActSuccess[Record Success result]
            CheckResponse -->|Step Limit Reached / Error| ReActFail[Record Fail result]
        end
    end

    LogIgnore --> NodeSumm
    ReActSuccess --> NodeSumm
    ReActFail --> NodeSumm
    
    NodeSumm --> End([End Pipeline / Print Summary])

    class Start,End startEnd;
    class InitMCP,CallMCP mcp;
    class NodeRead,NodePlan,NodeExec,NodeSumm lgraph;
    class LogIgnore,InitReAct,PromptLLM,FeedHistory,ReActSuccess,ReActFail process;
    class ForEach,CheckResponse decision;
```



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




