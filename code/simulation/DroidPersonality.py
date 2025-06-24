
import random
from typing import Any, Callable, List
from pydantic import BaseModel
from simulation.DroidComponents import DroidPersonality
from simulation.Component import Component, ToolCall
from simulation.Entity import Location
from simulation.World import World

# A DroidPersonality is a component that defines how a droid interacts with the world.
#  Specifically, it is an LLM agent that can make decisions based on the world state.

class DroidPersonalitySimple(DroidPersonality):
    pass

class DroidPersonalityRandom(DroidPersonality):
    def on_tick(self, world: World):

        # Check to see if we are currently busy w/ an active task or tool call
        # If there is no active tool call, then we can perform one
        #if self.active_tool_call:
        #  print (f"Active tool call: {self.active_tool_call.function_ptr.__name__}")
        #else:
        #  print("No active tool call, performing random action.")
        #  TODO: Move to a random entity or location, charge something, etc.
        
        # For now, the only action is to move, but can code in more complex actions later
        
        # Only think about moving when not currently moving
        if self.chassis.destination is not None:
            # Currently moving, so don't do anything new.
            return
        
        # Only think about moving when not currently moving
        self.think_interval += 1
        if self.think_timer < self.think_interval:
            # Not time to think yet, so do nothing
            return
        
        # We are done delaying, so now we can think about moving
        self.think_timer = 0.0
        self.think_interval = random.uniform(1.0, 3.0)  # Reset think interval

        # Get possible adjacent tiles
        adjacent_tiles = [
            self.chassis.location + Location(x=0, y=-1),  # Up
            self.chassis.location + Location(x=1, y=0),  # Right
            self.chassis.location + Location(x=0, y=1),  # Down
            self.chassis.location + Location(x=-1, y=0),  # Left
        ]
        
        # Filter valid tiles
        valid_tiles = []
        for tx, ty in adjacent_tiles:
            #if self.is_tile_valid(tx, ty):
            # TODO: World collision check ^
                valid_tiles.append((tx, ty))
        
        # Sometimes don't move (add current position as option)
        if random.random() < 0.3:  # 30% chance to stay put
            valid_tiles.append((self.tile_x, self.tile_y))
        
        # Choose a random valid tile
        target_location = random.choice(valid_tiles)
        if target_location != self.chassis.location:
            self.chassis.destination = target_location

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

