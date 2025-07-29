
# Information needed to call a function as a tool
#  This is used to define the tools that a Component provides to the agentic AI.
from enum import Enum
from typing import Any, Callable, List, Optional
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

class ToolCallState(Enum):
    IN_PROCESS = "in_process"
    SUCCESS = "success"
    FAILURE = "failure"

class ToolCallResult(BaseModel):
    # State is an enum that can be in_process, success, or failure
    state: ToolCallState = ToolCallState.IN_PROCESS
    message: Optional[str] = None # Optional message to provide additional context
    data: Optional[Any] = None    # Optional data returned by the tool call
    callback: Optional[Callable[[], "ToolCallResult"]] = None  # Optional callback to call when the tool call is complete

    def __init__(self, state: ToolCallState, message: str = None, data: Any = None, callback: Callable[[], "ToolCallResult"] = None):
        super().__init__(state=state, message=message, data=data)
        self.callback = callback
        if callback and not callable(callback):
            raise ValueError("Callback must be a callable function that returns a ToolCallResult.")
        
    def get_state(self) -> ToolCallState:
        """
        Get the current state of the tool call.
        Returns:
            ToolCallState: The current state of the tool call.
        """
        if self.callback:
            # If there is a callback, we need to call it to get the current state
            result = self.callback()
            if isinstance(result, ToolCallResult):
                self.state = result.state
                self.message = result.message
                self.data = result.data
                if result.callback:
                    self.callback = result.callback
            else:
                raise ValueError("Callback must return a ToolCallResult.")
        return self.state

class ToolCall(BaseModel):
    # Function pointer to the tool function.
    #  Returns a pointer to a function that takes no parameters and returns a ToolCallResult.
    function_ptr: Callable[..., ToolCallResult]
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
    
    def __init__(self, function_ptr: Callable[..., ToolCallResult]):
        # Use docstring_parser to extract the function's docstring and parameters
        docstring = parse(function_ptr.__doc__)
        # Assert that we have a short description
        if not docstring.short_description:
            raise ValueError(f"Function {function_ptr.__name__} must have a docstring with a short description.")
        description = docstring.short_description
        parameters = []
        for param in docstring.params:
            # Create a ToolCallParameter for each parameter in the function's docstring
            if not param.description:
                raise ValueError(f"Function {function_ptr.__name__} parameter '{param.arg_name}' must have a description.")
            if not param.type_name:
                raise ValueError(f"Function {function_ptr.__name__} parameter '{param.arg_name}' must have a Pydantic type specified.")

            parameters.append(
                ToolCallParameter(
                    name=param.arg_name,
                    description=param.description,
                    type=param.type_name,
                    required=True  # Assume all parameters are required by default
                )
            )

        super().__init__(function_ptr=function_ptr, description=description, parameters=parameters)

        # If the function has a return type, add it to the parameters
        # TODO: Are there tool call formats that expect this? OpenAI does not.
        # if docstring.returns:
