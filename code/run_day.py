# Simulates a day in the life of an EG-6 power droid.
import json

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
        }
    }
]

system_prompt = "You are an {model} {subtype}. Your name is '{name}'. Your ID is '{object_id}'. You use tools and functions to accomplish your daily tasks. Don't overthink things. Your purpose is to charge the batteries of equipment on the farm and ensure they are all supplied with power. You can recharge your own batteries at power stations to ensure you can carry enough power to charge the equipment. When everything is fully charged, and your own batteries are recharged, you can switch yourself off at the power station. You can move to specific locations or objects on the farm. You are a helpful and efficient droid, and you will do your best to complete your tasks. You will use the tools provided to you to accomplish your tasks. If you cannot complete a task, you will inform the user of the reason why. You will not make assumptions about the state of the farm or the equipment, and you will only use the information provided to you in this conversation."
sample_conversations = [
    { "user": "What is your name?", "assistant": "My name is {name}, and I am an {model} {subtype}." },
    { "user": "What is your purpose?", "assistant": "My purpose is to charge the batteries of equipment on the farm and ensure they are all supplied with power." },
    { "user": "How do you recharge your batteries?", "assistant": "I can recharge my own batteries at power stations to ensure I have enough power to charge the equipment." },
    { "user": "What tools do you have?", "assistant": "I have tools to charge equipment, recharge myself at power stations, and move to specific locations or objects on the farm." },
    { "user": "Which equipment should you charge first?", "assistant": "If I am below 30% battery, then I should travel to a power station and recharge myself first. If I am within 1 meter of equipment that is less than 90%, I should charge it. Otherwise, I should travel to the equipment with the lowest battery level and charge that next" },
    { "user": "How low should your battery be before you recharge yourself?", "assistant": "I should recharge myself when my battery level is below 30%." },
    { "user": "How low should the equipment's battery be before you charge it?", "assistant": "I should charge the equipment when its battery level is below 90%." },
    { "user": "What should you do at the end of the day?", "assistant": "At the end of the day, when all work is done and I am back at the power station, I should switch myself off." },
]

daily_prompt = "Current farm status: {farm_status}\nWhat is your next action?"

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


# Populate the "messages" list with the system prompt, sample conversations, and daily prompt
messages = [{"role": "system", "content": fill_vars(system_prompt, gonky)}]
for conversation in sample_conversations:
    messages.append({"role": "user", "content": conversation["user"]})
    messages.append({"role": "assistant", "content": fill_vars(conversation["assistant"], gonky)})

print ("######## Start of day simulation ########")
print (" Initial equipment status:", json.dumps(equipment, indent=2))
print (" Prompting model with system prompt and sample conversations:", json.dumps(messages, indent=2))

print ("######## End of setup ########")
running = True

while running:
    farm_status = populate_distance_from(equipment, gonky)
    messages.append({"role": "user", "content": fill_vars(daily_prompt, {"farm_status": json.dumps(farm_status)})})

    query = {
        "model": "gpt-4-turbo",
        "tools": tools,
        "tool_choice": "auto",
        "messages": messages,
        "temperature": 0.2
    }
    #print(f"Querying model with last message of: {json.dumps(messages[-1], indent=2)}")
    response = requests.post(endpoint, json=query)
    response_json = response.json()
    # Update our messages with the response from the model. Post any messages to the user, and then execute any tools that we need to call.
    for choice in response_json["choices"]:
        #print("Response from model:", json.dumps(choice, indent=2))
        if "message" in choice:
            # Append the assistant's message to the messages list
            messages.append(response_json["choices"][0]["message"])
            if "content" in choice["message"]:
                print(" Assistant: ", choice["message"]["content"])
            if "tool_calls" in choice["message"]:
                for tool_call in choice["message"]["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    params = json.loads(tool_call["function"]["arguments"])
                    print(f"Executing tool: {tool_name} with params: {params}")
                    tool_response = ""
                    # Execute the tool
                    if tool_name == "charge_equipment":
                        equipment_obj = obj_by_id(params["object_id"], equipment)
                        if equipment_obj and gonky["battery_level"] >= 10 and distance_between(equipment_obj, gonky) <= 1:
                            charge_need = 100 - equipment_obj["battery_level"]
                            charge_amount = min(gonky["battery_level"] - 10, charge_need)
                            gonky["battery_level"] -= charge_amount
                            equipment_obj["battery_level"] += charge_amount
                            tool_response = f"Charged {equipment_obj['object_id']} to {equipment_obj['battery_level']}%"
                        else:
                            tool_response = "Cannot charge equipment. Either too far away or not enough battery."
                    
                    elif tool_name == "recharge_self":
                        power_station = obj_by_id("power_station_1", equipment)
                        if power_station and distance_between(power_station, gonky) <= 1:
                            gonky["battery_level"] = 100
                            tool_response = "Recharged self to 100%"
                        else:
                            tool_response = "Cannot recharge self. Either too far away, or unable to find power station."
                    
                    elif tool_name == "move_to_location":
                        gonky["location"]["x"] = params["x"]
                        gonky["location"]["y"] = params["y"]
                        tool_response = f"Moved to location ({gonky['location']['x']}, {gonky['location']['y']})"
                    
                    elif tool_name == "move_to_object":
                        target_obj = obj_by_id(params["object_id"], equipment)
                        if target_obj:
                            gonky["location"]["x"] = target_obj["location"]["x"]
                            gonky["location"]["y"] = target_obj["location"]["y"]
                            tool_response = f"Moved to object {target_obj['object_id']} at location ({gonky['location']['x']}, {gonky['location']['y']})"
                        else:
                            tool_response = f"Cannot move to object. Unable to find object {params['object_id']}."
                    elif tool_name == "switch_self_off":
                        tool_response = "Switched self off."
                        running = False

                    print(f'Tool response: {tool_response}')
                    # Append the tool response to the messages list
                    tool_response_message = {
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": tool_name,
                        "content": tool_response,
                    }
                    messages.append(tool_response_message)
            else:
                print("######## ERROR: No tool calls in response. ########")
                running = False
                break
        else:
            print("######## ERROR: No message in response. ########")
            running = False
            break

    print(" Current equipment status:", json.dumps(equipment, indent=2))

print("######## End of day simulation ########")
print(" Final messages:", json.dumps(messages, indent=2))
print("#######################################")
print("Final equipment status:", json.dumps(equipment, indent=2))
print()
print("#######################################")
# Assert that Gonky's battery is at 100% and all equipment is charged to 100%
for eq in equipment:
    assert eq["battery_level"] == 100, f"{eq['object_id']}'s battery is not at 100%."
print("All equipment is fully charged and Gonky's battery is at 100%.")
print("Gonky has successfully completed its daily tasks!")