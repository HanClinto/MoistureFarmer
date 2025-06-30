
# Information needed to call a function as a tool
#  This is used to define the tools that a Component provides to the agentic AI.
from typing import Any, Callable, List
from pydantic import BaseModel


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
