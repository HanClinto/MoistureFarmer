# Simulates a day in the life of an EG-6 power droid.
import json
import os
import sys

# Initialize ANSI color support for Windows
def init_colors():
    """Initialize ANSI color support for cross-platform compatibility."""
    if os.name == 'nt':  # Windows
        try:
            # Enable ANSI escape sequences in Windows Console
            import subprocess
            subprocess.run('', shell=True, check=True)
            # For older Windows versions, try colorama
            try:
                import colorama
                colorama.init()
            except ImportError:
                # If colorama is not available, try enabling ANSI support directly
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except:
            pass
    
# Initialize colors at startup
init_colors()

def load_system_config(config_path="system_config.json"):
    """Load system prompt and sample conversations from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {config_path} not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing {config_path}: {e}")
        sys.exit(1)

gonky = {
        "object_id":"eg6_gonky",
        "type":"droid",
        "subtype":"power droid",
        "name":"Gonky",
        "model":"EG-6",
        "description":"EG-6 power droid",
        "location":{"x":0,"y":0},
        "battery_level":30
    }

equipment = [
        gonky,
        {"object_id":"vaporator_1","type":"vaporator","model":"GX-8","location":{"x":10,"y":15},"battery_level":50},
        #{"object_id":"vaporator_2","type":"vaporator","model":"GX-8","location":{"x":15,"y":10},"battery_level":20},
        #{"object_id":"vaporator_3","type":"vaporator","model":"GX-8","location":{"x":20,"y":15},"battery_level":80},
        {"object_id":"power_station_1","type":"power station","subtype":"medium fusion reactor power generator", "model":"MFCR-200","location":{"x":5,"y":5},"battery_level":100}
    ]

def obj_by_id(obj_id, objs):
    """Find an object by its ID in a list of objects."""
    for obj in objs:
        if obj["object_id"] == obj_id:
            return obj
    return None

tools = [
    {
        "type":"function",
        "function":{
            "name":"charge_equipment",
            "description":"Charge the batteries of a piece of equipment. Requires the id of the equipment. Must be within 1 meter distance. Must have at least 10% charge in self to charge other equipment.",
            "parameters":{
                "type":"object",
                "properties":{
                    "object_id":{
                        "type":"string",
                        "description":"The ID of the equipment to charge. Distance away must be 1 meter or less."
                    }
                },
                "required":["object_id"],
                "additionalProperties": False
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"recharge_self",
            "description":"Recharge your own batteries at a power station. No parameters required.",
            "parameters":{
                "type":"object",
                "properties":{},
                "required":[],
                "additionalProperties": False
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"move_to_location",
            "description":"Move to a specific location on the farm.",
            "parameters":{
                "type":"object",
                "properties":{
                    "x":{
                        "type":"integer",
                        "description":"The x coordinate to move to."
                    },
                    "y":{
                        "type":"integer",
                        "description":"The y coordinate to move to."
                    }
                },
                "required":["x", "y"],
                "additionalProperties": False
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"move_to_object",
            "description":"Move adjacent to the location of a specific object.",
            "parameters":{
                "type":"object",
                "properties":{
                    "object_id":{
                        "type":"string",
                        "description":"The ID of the object to move to."
                    }
                },
                "required":["object_id"],
                "additionalProperties": False
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"switch_self_off",
            "description":"Switch yourself off. Use at the end of the day when all work is done and we're back at the power station. No parameters required.",
            "parameters":{
                "type":"object",
                "properties":{},
                "required":[],
                "additionalProperties": False
            }
        }    }
]

# Load system configuration from JSON file
config = load_system_config()
system_prompt = config["system_prompt"]
sample_conversations = config["sample_conversations"] 
daily_prompt = config["daily_prompt"]


# Color codes that work cross-platform
class Colors:
    """Cross-platform color codes."""
    def __init__(self):
        # Check if we should use colors
        self.use_colors = self._should_use_colors()
        
        if self.use_colors:
            self.BOLD = '\033[1m'
            self.RESET = '\033[0m'
            self.ITALIC = '\033[3m'
            self.PURPLE = '\033[1;35m'
            self.YELLOW = '\033[1;33m'
            self.GREEN = '\033[1;32m'
        else:
            # No colors - just use empty strings
            self.BOLD = ''
            self.RESET = ''
            self.ITALIC = ''
            self.PURPLE = ''
            self.YELLOW = ''
            self.GREEN = ''
    
    def _should_use_colors(self):
        """Determine if we should use colors based on environment."""
        # Don't use colors if output is redirected
        if not sys.stdout.isatty():
            return False
            
        # Check environment variables
        if os.environ.get('NO_COLOR'):
            return False
            
        if os.environ.get('FORCE_COLOR'):
            return True
            
        # Check for common terminals that support colors
        term = os.environ.get('TERM', '').lower()
        if any(term_type in term for term_type in ['color', 'ansi', 'xterm', 'screen', 'tmux']):
            return True
            
        # On Windows, check if we're in a modern terminal
        if os.name == 'nt':
            # Check for Windows Terminal, VS Code terminal, or other modern terminals
            wt_session = os.environ.get('WT_SESSION')
            term_program = os.environ.get('TERM_PROGRAM', '').lower()
            if wt_session or 'vscode' in term_program:
                return True
                
        return True  # Default to using colors

# Initialize colors
colors = Colors()

def print_single_message(msg):
    """Print a single message in the formatted style."""
    role = msg.get("role", "unknown")
    content = msg.get("content", "")
    
    if role == "system":
        print(f"\n{colors.PURPLE}System>{colors.RESET} {content.strip()}")
    elif role == "user":
        print(f"\n{colors.YELLOW}User>{colors.RESET} {content.strip()}")
    elif role == "assistant":
        # Only print content if it's not empty or None
        if content and content.strip():
            print(f"\n{colors.GREEN}Droid>{colors.RESET} {content.strip()}")
        
        # Check for tool calls
        if "tool_calls" in msg:
            for tool_call in msg["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                try:
                    params = json.loads(tool_call["function"]["arguments"])
                    param_str = ", ".join([f"{k}: {v}" for k, v in params.items()])
                    print(f"    {colors.ITALIC}Droid {tool_name} ({param_str}){colors.RESET}")
                except:
                    print(f"    {colors.ITALIC}Droid {tool_name} (invalid params){colors.RESET}")
    elif role == "tool":
        tool_name = msg.get("name", "unknown_tool")
        print(f"    {colors.ITALIC}{content}{colors.RESET}")

def print_formatted_chat(messages):
    """Print the chat messages in a nicely formatted way."""
    for msg in messages:
        print_single_message(msg)
    

def fill_vars(prompt, obj):
    """Fill in the variables in the prompt with the values from the object."""
    return prompt.format(**obj)

def distance_between(obj1, obj2):
    """Calculate the Manhattan distance from one object to another"""
    if "location" in obj1 and "location" in obj2:
        return abs(obj1["location"]["x"] - obj2["location"]["x"]) + abs(obj1["location"]["y"] - obj2["location"]["y"])

    # Throw an exception

def populate_distance_from(objs, self):
    """Calculate the Manhattan distance from self to each object."""
    # Duplicate the list to avoid modifying the original
    objs = json.loads(json.dumps(objs))
    for obj in objs:
        # Skip self object
        if obj["object_id"] == self["object_id"]:
            continue
        if "location" in obj:
            obj["distance_from_self"] = distance_between(obj, self)
    return objs


import requests

endpoint = "http://localhost:8080/v1/chat/completions"

# Tool implementations
def charge_equipment_tool(params, gonky, equipment):
    """Execute the charge_equipment tool."""
    equipment_obj = obj_by_id(params["object_id"], equipment)
    if equipment_obj and gonky["battery_level"] >= 10 and distance_between(equipment_obj, gonky) <= 1:
        charge_need = 100 - equipment_obj["battery_level"]
        charge_amount = min(gonky["battery_level"] - 10, charge_need)
        gonky["battery_level"] -= charge_amount
        equipment_obj["battery_level"] += charge_amount
        return f"Charged {equipment_obj['object_id']} to {equipment_obj['battery_level']}%", False
    else:
        return "Cannot charge equipment. Either too far away or not enough battery.", False

def recharge_self_tool(params, gonky, equipment):
    """Execute the recharge_self tool."""
    power_station = obj_by_id("power_station_1", equipment)
    if power_station and distance_between(power_station, gonky) <= 1:
        gonky["battery_level"] = 100
        return "Recharged self to 100%", False
    else:
        return "Cannot recharge self. Either too far away, or unable to find power station.", False

def move_to_location_tool(params, gonky, equipment):
    """Execute the move_to_location tool."""
    gonky["location"]["x"] = params["x"]
    gonky["location"]["y"] = params["y"]
    return f"Moved to location ({gonky['location']['x']}, {gonky['location']['y']})", False

def move_to_object_tool(params, gonky, equipment):
    """Execute the move_to_object tool."""
    target_obj = obj_by_id(params["object_id"], equipment)
    if target_obj:
        gonky["location"]["x"] = target_obj["location"]["x"]
        gonky["location"]["y"] = target_obj["location"]["y"]
        return f"Moved to object {target_obj['object_id']} at location ({gonky['location']['x']}, {gonky['location']['y']})", False
    else:
        return f"Cannot move to object. Unable to find object {params['object_id']}.", False

def switch_self_off_tool(params, gonky, equipment):
    """Execute the switch_self_off tool."""
    return "Switched self off.", True

# Global tool map
tool_implementations = {
    "charge_equipment": charge_equipment_tool,
    "recharge_self": recharge_self_tool,
    "move_to_location": move_to_location_tool,
    "move_to_object": move_to_object_tool,
    "switch_self_off": switch_self_off_tool
}

# Load system configuration from JSON file
config = load_system_config()
system_prompt = config["system_prompt"]
sample_conversations = config["sample_conversations"] 
daily_prompt = config["daily_prompt"]

# Populate the "messages" list with the system prompt, sample conversations, and daily prompt
messages = [{"role": "system", "content": fill_vars(system_prompt, gonky)}]
for conversation in sample_conversations:
    messages.append({"role": "user", "content": conversation["user"]})
    messages.append({"role": "assistant", "content": fill_vars(conversation["assistant"], gonky)})

print ("######## Start of day simulation ########")
print (" Prompting model with system prompt and sample conversations:")
print_formatted_chat(messages)

print ("######## End of setup ########")
running = True

iteration_count = 0
error_count = 0

def print_equipment_table(equipment):
    """Print equipment status as a formatted table."""
    print(f"{'object_id':<18} {'model':<10} {'location':<15} {'battery_level':<14}")
    print("-" * 60)
    for eq in equipment:
        loc = f"({eq['location']['x']},{eq['location']['y']})" if 'location' in eq else "N/A"
        print(f"{eq['object_id']:<18} {eq.get('model', 'N/A'):<10} {loc:<15} {eq['battery_level']:<14}")
while running:
    iteration_count += 1
    print()
    print(f"######## Iteration {iteration_count} ########")
    farm_status = populate_distance_from(equipment, gonky)
    messages.append({"role": "user", "content": fill_vars(daily_prompt, {"farm_status": json.dumps(farm_status)})})

    # Print equipment status as a table
    print_equipment_table(equipment)

    # print("Agent is thinking about its next action...")
    print("")

    # Prepare the query to the model
    query = {
        "model": "gpt-4-turbo",
        "tools": tools,
        "tool_choice": "auto",
        "messages": messages,
        "temperature": 0.2
    }
    #print(f"Querying model with last message of: {json.dumps(messages[-1], indent=2)}")
    response_json = requests.post(endpoint, json=query).json()

    # Update our messages with the response from the model. Post any messages to the user, and then execute any tools that we need to call.
    for choice in response_json["choices"]:
        #print("Response from model:", json.dumps(choice, indent=2))
        if "message" in choice:
            # Append the assistant's message to the messages list
            assistant_message = response_json["choices"][0]["message"]
            messages.append(assistant_message)
            
            # Print the assistant's message using formatted output
            print_single_message(assistant_message)
            
            if "tool_calls" in choice["message"]:
                for tool_call in choice["message"]["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    params = json.loads(tool_call["function"]["arguments"])
                    
                    # Execute the tool using the global tool map
                    if tool_name in tool_implementations:
                        tool_response, should_stop = tool_implementations[tool_name](params, gonky, equipment)
                        if should_stop:
                            running = False
                    else:
                        tool_response = f"Unknown tool: {tool_name}"

                    # Append the tool response to the messages list
                    tool_response_message = {
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": tool_name,
                        "content": tool_response,
                    }
                    messages.append(tool_response_message)
                    
                    # Print the tool response using formatted output
                    print_single_message(tool_response_message)
            else:
                print("######## ERROR: No tool calls in response. ########")
                error_count += 1
                running = False
                break
        else:
            print("######## ERROR: No message in response. ########")
            error_count += 1
            running = False
            break

print()
print()
print("######## End of day simulation ########")
print("\n" + "="*50)
print("CHAT HISTORY")
print("="*50)
print_formatted_chat(messages)
print("\n" + "="*50)
print("#######################################")
print("Final equipment status:")
print_equipment_table(equipment)
print()
print("#######################################")
# Assert that all equipment and droids are charged to 100%
for eq in equipment:
    assert eq["battery_level"] == 100, f"{eq['object_id']}'s battery is not at 100%."
print("All equipment is fully charged and Gonky's battery is at 100%.")
print("Gonky has successfully completed its daily tasks!")