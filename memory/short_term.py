import os
import json
from typing import Dict, Any

class MemoryManager:
    """Manages short-term persistent JSON-based memory cache for the agent."""

    def __init__(self, memory_file: str = "agent_session_memory.json"):
        self.memory_file = memory_file
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        """Loads data from the memory file or returns empty dict if it does not exist/is invalid."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieves a value from memory."""
        return self.data.get(key, default)

    def set(self, key: str, value: Any):
        """Sets a value in memory and saves it immediately to the persistent store."""
        self.data[key] = value
        self._save()

    def _save(self):
        """Writes current data to the memory file."""
        try:
            with open(self.memory_file, "w") as f:
                json.dump(self.data, f, indent=4)
        except OSError as e:
            print(f"⚠️ Warning: Could not write memory to file: {e}")

    def get_summary(self) -> str:
        """Returns a string summary of the memory for the system prompt."""
        last_checked = self.get("last_time_checked")
        if last_checked:
            return f"According to file logs, the user last checked the time at: {last_checked}"
        return "No previous interaction logs found in the file."

    def clear(self):
        """Clears memory file and internal data."""
        self.data = {}
        if os.path.exists(self.memory_file):
            try:
                os.remove(self.memory_file)
            except OSError:
                pass
