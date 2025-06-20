# Simulates a day in the life of an EG-6 power droid.
import json
import sys
from Color import Colors
from llm_tools import tools
from simulation import Simulation
from llm_thread import LlmThread
from llm_console import LlmConsole

# Initialize colors at startup
colors = Colors()

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

def main():
    # Load system configuration from JSON file
    config = load_system_config()
    system_prompt = config["system_prompt"]
    sample_conversations = config["sample_conversations"] 
    daily_prompt = config["daily_prompt"]

    sim = Simulation()
    llm_thread = LlmThread(system_prompt, sample_conversations, sim.gonky)
    llm_console = LlmConsole(colors)

    # Global tool map
    tool_implementations = {
        "charge_equipment": sim.charge_equipment,
        "recharge_self": sim.recharge_self,
        "move_to_location": sim.move_to_location,
        "move_to_object": sim.move_to_object,
        "switch_self_off": sim.switch_self_off
    }

    print ("######## Start of day simulation ########")
    print (" Prompting model with system prompt and sample conversations:")
    llm_console.print_formatted_chat(llm_thread.messages)

    print ("######## End of setup ########")
    running = True

    iteration_count = 0
    error_count = 0

    while running:
        iteration_count += 1
        print()
        print(f"######## Iteration {iteration_count} ########")
        farm_status = sim.populate_distance_from_self()
        
        # Print equipment status as a table
        llm_console.print_equipment_table(sim.equipment)

        print("")

        try:
            response_json = llm_thread.get_completion(daily_prompt, farm_status, tools)
        except Exception as e:
            print(f"Error calling LLM API: {e}")
            error_count += 1
            running = False
            break

        # Update our messages with the response from the model. Post any messages to the user, and then execute any tools that we need to call.
        for choice in response_json["choices"]:
            if "message" in choice:
                # The assistant's message is already in the thread, so we just print it
                assistant_message = choice["message"]
                llm_console.print_single_message(assistant_message)
                
                if "tool_calls" in choice["message"]:
                    for tool_call in choice["message"]["tool_calls"]:
                        tool_name = tool_call["function"]["name"]
                        params = json.loads(tool_call["function"]["arguments"])
                        
                        # Execute the tool using the global tool map
                        if tool_name in tool_implementations:
                            tool_response, should_stop = tool_implementations[tool_name](params)
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
                        llm_thread.add_tool_response(tool_response_message)
                        
                        # Print the tool response using formatted output
                        llm_console.print_single_message(tool_response_message)
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
    llm_console.print_formatted_chat(llm_thread.messages)
    print("\n" + "="*50)
    print("#######################################")
    print("Final equipment status:")
    llm_console.print_equipment_table(sim.equipment)
    print()
    print("#######################################")
    # Assert that all equipment and droids are charged to 100%
    for eq in sim.equipment:
        assert eq["battery_level"] == 100, f"{eq['object_id']}'s battery is not at 100%."
    print("All equipment is fully charged and Gonky's battery is at 100%.")
    print("Gonky has successfully completed its daily tasks!")

if __name__ == "__main__":
    main()