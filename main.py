import sys
from agent import AgentLoop, AgentState

# ANSI Color Codes
COLOR_BLUE = "\033[94m"
COLOR_GREEN = "\033[92m"
COLOR_MAGENTA = "\033[95m"
COLOR_YELLOW = "\033[93m"
COLOR_BOLD = "\033[1m"
COLOR_RESET = "\033[0m"

def print_color(text: str, color_code: str, end: str = "\n"):
    """Prints colored text if stdout is a terminal, otherwise falls back to plain text."""
    if sys.stdout.isatty():
        sys.stdout.write(f"{color_code}{text}{COLOR_RESET}{end}")
    else:
        sys.stdout.write(f"{text}{end}")
    sys.stdout.flush()

def show_banner():
    """Renders a beautiful ASCII header banner for the interactive shell."""
    banner = f"""
{COLOR_BOLD}{COLOR_BLUE}=============================================================
🤖  SIMPLE CLI AGENT WITH PERSISTENT MEMORY & TOOLS
============================================================={COLOR_RESET}
Interactive session started. Talk to the agent below!

{COLOR_BOLD}Session Shortcuts:{COLOR_RESET}
  • Type {COLOR_YELLOW}exit{COLOR_RESET} or {COLOR_YELLOW}quit{COLOR_RESET} to close the chat.
  • Type {COLOR_YELLOW}clear-mem{COLOR_RESET} to clear the persistent memory log.
=============================================================
"""
    print(banner)

def main():
    try:
        loop = AgentLoop()
    except Exception as e:
        print_color(f"❌ Error initializing Agent Engine: {e}", COLOR_YELLOW)
        sys.exit(1)

    # Check if arguments were passed (single-shot execution mode)
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
        print_color(f"👤 User: {user_prompt}", COLOR_GREEN)
        try:
            # Single-shot execution doesn't persist interactive message history, but preserves file memory.
            state = AgentState()
            response = loop.run_turn(user_prompt, state)
            print_color(f"🤖 Agent: {response}", COLOR_MAGENTA)
        except Exception as e:
            print_color(f"❌ Execution error: {e}", COLOR_YELLOW)
            sys.exit(1)
        sys.exit(0)

    # Otherwise, start interactive session mode
    show_banner()
    state = AgentState()
    
    while True:
        try:
            print_color("👤 User: ", COLOR_GREEN, end="")
            user_input = input().strip()
            
            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit"):
                print_color("\n👋 Goodbye!", COLOR_BLUE)
                break

            if user_input.lower() == "clear-mem":
                loop.memory.clear()
                # Clear chat history and step counters by re-initializing state
                state = AgentState()
                print_color("🧹 Memory and session state cleared successfully.", COLOR_YELLOW)
                print_color("=============================================================", COLOR_BLUE)
                continue

            # Run agent turn with persistent interactive session state
            response = loop.run_turn(user_input, state)
            print_color(f"🤖 Agent: {response}", COLOR_MAGENTA)
            print_color("-------------------------------------------------------------", COLOR_BLUE)

        except (KeyboardInterrupt, EOFError):
            print_color("\n👋 Goodbye!", COLOR_BLUE)
            break
        except Exception as e:
            print_color(f"❌ Error: {e}", COLOR_YELLOW)
            print_color("-------------------------------------------------------------", COLOR_BLUE)

if __name__ == "__main__":
    main()