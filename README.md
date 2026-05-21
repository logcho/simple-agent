# 🤖 Simple AI Agent Framework

A lightweight, highly modular, and extensible Python framework for building autonomous AI agents with access to persistent memory and tool execution. The architecture follows a strict separation of concerns, decoupling configuration, prompt templates, tools, storage adapters, and the cognitive loop.

---

## 📂 Repository File Structure

The project is structured as follows to allow clean modular scaling:

```
simple-agent/
├── .env                  # Secure API credentials (ignored by git)
├── requirements.txt      # System packages (openai, PyYAML)
├── config.yaml           # Hyperparameters, model settings, and storage paths
├── main.py               # CLI Application entry point
│
├── agent/                # Cognitive Engine
│   ├── __init__.py       # Exposes core classes (AgentLoop, AgentState)
│   ├── loop.py           # Cognitive execution loop (Thought -> Action -> Observation)
│   └── state.py          # Session history and execution step manager
│
├── prompts/              # System Persona Layer (Plain text templates)
│   ├── system_prompt.txt # Master behavioral persona and constraints
│   └── tool_prompt.txt   # Instructions directing formatting of tool calls
│
├── tools/                # Action Tier (Modular Skill Plugins)
│   ├── __init__.py       # Combines separate functions into a unified toolkit array
│   └── time_tool.py      # Real-world server time helper (example tool)
│
└── memory/               # Storage Layer (Context & Knowledge cache)
    ├── __init__.py       # Exposes memory adapters
    └── short_term.py     # Simple session-persistent JSON cache manager
```

---

## ⚙️ Getting Started

### 1. Installation

Clone the repository and install the dependencies in a virtual environment:

```bash
# Activate your virtual environment
source venv/bin/activate

# Install the required packages
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the root directory and add your OpenAI API Key:

```env
OPENAI_API_KEY=your-actual-api-key-here
```

Adjust the agent behavior or change the LLM model inside `config.yaml`:

```yaml
model: "gpt-4o-mini"
temperature: 0.0
memory_file: "agent_session_memory.json"
```

### 3. Running the Agent

You can execute the agent in two different modes:

#### **Interactive CLI Mode (Recommended)**
Run without arguments to enter an interactive shell where conversation context is preserved across turns:

```bash
python main.py
```
*Shortcuts during session:*
- Type `exit` or `quit` to close the shell.
- Type `clear-mem` to clear the persistent JSON memory and reset the conversation history.

#### **Single-shot Execution Mode**
Pass a query as arguments to run a single turn and exit:

```bash
python main.py "What time is it?"
```

---

## 🧠 Core Cognitive Loop (Thought ➔ Action ➔ Observation)

The agent runs an iterative execution loop implemented in `agent/loop.py`:

```
          ┌──────────────────────────────────────────┐
          │               User Input                 │
          └────────────────────┬─────────────────────┘
                               │
                               ▼
        ┌──────────────────────────────────────────────┐
        │  Read dynamic prompt (inject short-term mem)  │
        └──────────────────────┬───────────────────────┘
                               │
                               ▼
    ┌──────────────────────────────────────────────────────┐
    │  Execute LLM Completion (Thought / Action Decision)  │◄─────────┐
    └──────────────────────────┬───────────────────────────┘          │
                               │                                      │
               Is there a tool call requested?                        │
                     /                   \                            │
                   YES                    NO                          │
                   /                        \                         │
                  ▼                          ▼                        │
       ┌───────────────────────┐   ┌───────────────────┐    ┌─────────┴─────────┐
       │     Action Stage      │   │    Final Text     │    │    Observation    │
       │ (Execute tool method) │   │     Response      │    │ (Append tool msg  │
       └──────────┬────────────┘   └───────────────────┘    │  to chat history) │
                  │                                         └─────────▲─────────┘
                  └───────────────────────────────────────────────────┘
```

1. **Thought:** The LLM receives the system guidelines, memory log, and conversation state, then plans the next action.
2. **Action:** If the model requires external information, it requests a function execution. The `AgentLoop` executes the respective Python function in the `tools/` tier.
3. **Observation:** The execution result is packaged and sent back to the model, allowing it to complete its reasoning and formulate the final response.

---

## 🛠️ How to Build & Extend Agents

This codebase is designed so you can create new capabilities easily without modifying the orchestration engine.

### 1. Adding a New Tool (Action)

To add a new tool, define the function inside a file in the `tools/` directory and register it:

1. **Write the tool** (e.g. `tools/web_search.py`):
   ```python
   # tools/web_search.py
   def web_search(query: str) -> str:
       """Search the web for information."""
       # Implement API call...
       return f"Search results for: {query}"
   ```

2. **Register the tool** in [tools/__init__.py](file:///Users/loganchoi/Desktop/simple-agent/tools/__init__.py):
   ```python
   from tools.web_search import web_search

   # 1. Add schema to TOOLS_SCHEMA
   TOOLS_SCHEMA.append({
       "type": "function",
       "function": {
           "name": "web_search",
           "description": "Search the web for information.",
           "parameters": {
               "type": "object",
               "properties": {
                   "query": {"type": "string"}
               },
               "required": ["query"]
           }
       }
   })

   # 2. Add mapping to TOOL_FUNCTIONS
   TOOL_FUNCTIONS["web_search"] = web_search
   ```

> [!TIP]
> **Dependency Injection:** If your tool requires access to the persistent memory registry, simply declare `memory_manager: MemoryManager` in the function's parameters. The `AgentLoop` uses python signature inspection to automatically inject it at runtime:
> ```python
> def get_current_time(memory_manager: MemoryManager) -> str:
>     ...
> ```

### 2. Modifying Prompts (Persona)

You can alter the behavior, instructions, or strict constraints of the agent by editing:
- `prompts/system_prompt.txt`: To update instructions or persona rules. Preserve the `{historical_log}` token, which is where persistent memory context is injected.
- `prompts/tool_prompt.txt`: To refine how the model thinks about and structures parameter calls.

### 3. Adding Alternative Memory Storage (Storage Layer)

To scale memory beyond a JSON file (e.g., adding a vector database for semantic memory, or a graph database):
1. Implement your new adapter inside `memory/` (e.g., `memory/semantic_vector.py`).
2. Add reference methods in `memory/__init__.py`.
3. Read the storage database connection credentials using values added to `config.yaml` or `.env`.
