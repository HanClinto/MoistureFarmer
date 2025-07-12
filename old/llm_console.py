import json

class LlmConsole:
    def __init__(self, colors):
        self.colors = colors

    def print_single_message(self, msg):
        """Print a single message in the formatted style."""
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        
        if role == "system":
            print(f"\n{self.colors.PURPLE}System>{self.colors.RESET} {content.strip()}")
        elif role == "user":
            print(f"\n{self.colors.YELLOW}User>{self.colors.RESET} {content.strip()}")
        elif role == "assistant":
            # Only print content if it's not empty or None
            if content and content.strip():
                print(f"\n{self.colors.GREEN}Droid>{self.colors.RESET} {content.strip()}")
            
            # Check for tool calls
            if "tool_calls" in msg:
                for tool_call in msg["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    try:
                        params = json.loads(tool_call["function"]["arguments"])
                        param_str = ", ".join([f"{k}: {v}" for k, v in params.items()])
                        print(f"    {self.colors.ITALIC}Droid {tool_name} ({param_str}){self.colors.RESET}")
                    except:
                        print(f"    {self.colors.ITALIC}Droid {tool_name} (invalid params){self.colors.RESET}")
        elif role == "tool":
            tool_name = msg.get("name", "unknown_tool")
            print(f"    {self.colors.ITALIC}{content}{self.colors.RESET}")

    def print_formatted_chat(self, messages):
        """Print the chat messages in a nicely formatted way."""
        for msg in messages:
            self.print_single_message(msg)

    def print_equipment_table(self, equipment):
        """Print equipment status as a formatted table."""
        print(f"{'object_id':<18} {'model':<10} {'location':<15} {'battery_level':<14}")
        print("-" * 60)
        for eq in equipment:
            loc = f"({eq['location']['x']},{eq['location']['y']})" if 'location' in eq else "N/A"
            print(f"{eq['object_id']:<18} {eq.get('model', 'N/A'):<10} {loc:<15} {eq['battery_level']:<14}")
