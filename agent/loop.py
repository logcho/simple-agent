import os
import yaml
import json
import inspect
from openai import OpenAI
from typing import Optional, Dict, Any

from agent.state import AgentState
from memory import MemoryManager
from tools import TOOLS_SCHEMA, TOOL_FUNCTIONS

def load_env(env_path: str = ".env"):
    """Loads environment variables from a .env file if it exists."""
    if os.path.exists(env_path):
        try:
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, val = line.split("=", 1)
                        os.environ[key.strip()] = val.strip().strip('"').strip("'")
        except OSError as e:
            print(f"⚠️ Warning: Could not read environment file {env_path}: {e}")

class AgentLoop:
    """The core execution engine running the Thought -> Action -> Observation loop."""

    def __init__(self, config_path: str = "config.yaml"):
        # Load configurations
        self.config = self._load_config(config_path)

        # Load environment credentials
        if not os.environ.get("OPENAI_API_KEY"):
            load_env()

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set.\n"
                "Please configure it in a .env file or export it in your shell environment."
            )

        self.client = OpenAI(api_key=api_key)
        
        # Instantiate memory layer using path from config
        memory_file = self.config.get("memory_file", "agent_session_memory.json")
        self.memory = MemoryManager(memory_file)

        # Prompts paths
        self.system_prompt_path = "prompts/system_prompt.txt"
        self.tool_prompt_path = "prompts/tool_prompt.txt"

    def _load_config(self, path: str) -> Dict[str, Any]:
        """Loads configuration dictionary from config.yaml, falling back to defaults."""
        defaults = {
            "model": "gpt-4o-mini",
            "temperature": 0.0,
            "memory_file": "agent_session_memory.json"
        }
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    loaded = yaml.safe_load(f)
                    if isinstance(loaded, dict):
                        defaults.update(loaded)
            except Exception as e:
                print(f"⚠️ Warning: Could not parse config file {path}: {e}. Using defaults.")
        return defaults

    def get_system_instructions(self) -> str:
        """Retrieves and constructs system prompts dynamically from prompts files and memory state."""
        system_prompt = "You are a helpful assistant."
        if os.path.exists(self.system_prompt_path):
            try:
                with open(self.system_prompt_path, "r") as f:
                    system_prompt = f.read()
            except OSError as e:
                print(f"⚠️ Warning: Could not read system prompt file: {e}")

        # Inject persistent memory summary
        memory_summary = self.memory.get_summary()
        system_prompt = system_prompt.replace("{historical_log}", memory_summary)

        # Append tool guidance instructions if available
        if os.path.exists(self.tool_prompt_path):
            try:
                with open(self.tool_prompt_path, "r") as f:
                    tool_prompt = f.read()
                    system_prompt += f"\n\n{tool_prompt}"
            except OSError:
                pass

        return system_prompt

    def run_turn(self, user_prompt: str, state: AgentState) -> str:
        """Runs the loop (Thought -> Action -> Observation) until a final text response is produced."""
        system_instructions = self.get_system_instructions()

        # Update or set the first message as our dynamic system instructions
        if not state.chat_history:
            state.add_message("system", system_instructions)
        else:
            state.chat_history[0]["content"] = system_instructions

        # Record User's request
        state.add_message("user", user_prompt)

        # Start execution loop
        while True:
            state.increment_step()

            # Thought & Action generation
            response = self.client.chat.completions.create(
                model=self.config.get("model", "gpt-4o-mini"),
                messages=state.chat_history,
                tools=TOOLS_SCHEMA,
                temperature=self.config.get("temperature", 0.0)
            )

            message = response.choices[0].message
            
            # Record Assistant Thought/Action in chat logs
            # Convert object to dict to keep state history structure plain
            assistant_msg = {
                "role": message.role,
                "content": message.content,
            }
            if message.tool_calls:
                assistant_msg["tool_calls"] = message.tool_calls
            
            state.chat_history.append(assistant_msg)

            if message.tool_calls:
                # Execution / Action Tier
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments or "{}")

                    print(f"📦 [System Executing '{tool_name}' tool (Step {state.current_step})...]")

                    if tool_name in TOOL_FUNCTIONS:
                        func = TOOL_FUNCTIONS[tool_name]

                        # Check if function signature requests MemoryManager injection
                        sig = inspect.signature(func)
                        kwargs = {}
                        if "memory_manager" in sig.parameters:
                            kwargs["memory_manager"] = self.memory
                        
                        # Merge other arguments
                        kwargs.update(tool_args)

                        try:
                            tool_result = func(**kwargs)
                        except Exception as e:
                            tool_result = f"Error executing tool '{tool_name}': {e}"
                    else:
                        tool_result = f"Error: Tool '{tool_name}' not found."

                    print(f"🤖 Agent (Tool Result): {tool_result}")

                    # Record Observation
                    state.add_message(
                        role="tool",
                        content=tool_result,
                        tool_call_id=tool_call.id,
                        name=tool_name
                    )
                # Loop back to evaluate observation and yield next thought/action
                continue
            else:
                # Final response reached
                return message.content or ""
