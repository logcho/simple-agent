from datetime import datetime
from memory import MemoryManager

def get_current_time(memory_manager: MemoryManager) -> str:
    """Returns the current real-world date and time, and updates persistent memory."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    memory_manager.set("last_time_checked", now)
    return f"The current server time is {now}."
