
from typing import Any, Callable, List
from pydantic import BaseModel
from simulation.DroidComponents import DroidPersonality
from simulation.Component import Component, ToolCall
from simulation.World import World

# A DroidPersonality is a component that defines how a droid interacts with the world.
#  Specifically, it is an LLM agent that can make decisions based on the world state.

class DroidPersonalitySimple(DroidPersonality):
    pass

class DroidPersonalityRandom(DroidPersonality):
    """
    A simple random personality that makes random decisions.
    This is a placeholder for more complex personalities.
    """
    def on_tick(self, world: World):
        pass

        # Check to see if we have an active task or tool call

        # If there is no active tool call, then we can perform one
        #if self.active_tool_call:
        #  print (f"Active tool call: {self.active_tool_call.function_ptr.__name__}")
        #else:
        #  print("No active tool call, performing random action.")
        #  TODO: Move to a random entity or location, charge something, etc.


class DroidPersonalitySimplePowerDroid(DroidPersonalitySimple):
    pass


# Information needed to call a function as a tool
#  This is used to define the tools that a Component provides to the agentic AI.
class ToolCallParameter(BaseModel):
    name: str
    description: str
    type: str  # Type of the parameter, e.g., "integer", "string", etc.
    required: bool = True  # Whether the parameter is required or optional

class ToolCall(BaseModel):
    function_ptr: Callable[..., Any]
    description: str
    parameters: List[ToolCallParameter]  # Parameter names and their descriptions

    # serialize to JSON in the format expected by the LLM
    # example:
    """
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
                "additionalProperties": false
            }
        }
    },
    """
    def to_llm_json(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.function_ptr.__name__,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {param.name: {"type": param.type, "description": param.description} for param in self.parameters},
                    "required": [param.name for param in self.parameters if param.required],
                    "additionalProperties": False
                }
            }
        }

