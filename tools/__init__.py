from typing import Dict, Callable, List, Any
from tools.time_tool import get_current_time

# Unified toolkit array for OpenAI
TOOLS_SCHEMA: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current server date and time."
        }
    }
]

# Map of tool names to Python functions
TOOL_FUNCTIONS: Dict[str, Callable] = {
    "get_current_time": get_current_time
}
