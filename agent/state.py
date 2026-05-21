from typing import List, Dict, Any, Optional

class AgentState:
    """Tracks current step, execution state, and conversation message log for the agent session."""

    def __init__(self, chat_history: Optional[List[Dict[str, Any]]] = None):
        self.chat_history = chat_history if chat_history is not None else []
        self.current_step = 0
        self.metadata: Dict[str, Any] = {}

    def increment_step(self):
        """Increments the internal cognitive execution step counter."""
        self.current_step += 1

    def add_message(self, role: str, content: Optional[str], **kwargs):
        """Helper to append a raw message to the execution chat log."""
        msg = {"role": role, "content": content}
        msg.update(kwargs)
        self.chat_history.append(msg)
        return msg
