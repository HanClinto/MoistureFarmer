
# Information needed to call a function as a tool
#  This is used to define the tools that a Component provides to the agentic AI.
from typing import Any, Callable, List
from pydantic import BaseModel
from docstring_parser import parse

_IS_TOOL_FUNCTION = "_is_tool_function"

# Decorator to mark a method as a tool function
#  This allows the method to be recognized as a tool that can be called by an Agent
# Note: Any function marked as a tool MUST have a complete docstring
#  that describes itself and its parameters, with Pydantic types and descriptions for all
def tool(func):
    setattr(func, _IS_TOOL_FUNCTION, True)
    if not func.__doc__:
        raise ValueError(f"Function {func.__name__} must have a docstring if it is going to be used as a tool.")
    return func

class ToolCallParameter(BaseModel):
    name: str
    description: str
    type: str  # Type of the parameter, e.g., "integer", "string", etc.
    required: bool = True  # Whether the parameter is required or optional

class ToolCall(BaseModel):
    function_ptr: Callable[..., Any]
    description: str
    parameters: List[ToolCallParameter]  # Parameter names and their descriptions
    # TODO: Add a way to check to see if the tool call has completed successfully (did we reach our destination? Did we charge our target?)

    def execute(self, *args, **kwargs) -> Any:
        """
        Execute the tool function with the provided arguments.
        This method is used to call the function as a tool.
        """
        return self.function_ptr(*args, **kwargs)

    # serialize to JSON in the format expected by the LLM
    # OpenAI format: 
    #  https://platform.openai.com/docs/guides/function-calling?api-mode=responses&strict-mode=enabled#defining-functions
    #  https://cookbook.openai.com/examples/how_to_call_functions_with_chat_models
    def to_openai_json(self) -> dict:
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
    
    def __init__(self, function_ptr: Callable[..., Any]):
        # Use docstring_parser to extract the function's docstring and parameters
        docstring = parse(function_ptr.__doc__)
        self.function_ptr = function_ptr
        # Assert that we have a short description
        if not docstring.short_description:
            raise ValueError(f"Function {function_ptr.__name__} must have a docstring with a short description.")
        self.description = docstring.short_description
        self.parameters = []
        for param in docstring.params:
            # Create a ToolCallParameter for each parameter in the function's docstring
            if not param.description:
                raise ValueError(f"Function {function_ptr.__name__} parameter '{param.arg_name}' must have a description.")
            if not param.type_name:
                raise ValueError(f"Function {function_ptr.__name__} parameter '{param.arg_name}' must have a Pydantic type specified.")

            self.parameters.append(
                ToolCallParameter(
                    name=param.arg_name,
                    description=param.description,
                    type=param.type_name,
                    required=True  # Assume all parameters are required by default
                )
            )
        # If the function has a return type, add it to the parameters
        # TODO: Are there tool call formats that expect this? OpenAI does not.
        # if docstring.returns:
