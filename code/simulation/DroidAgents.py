import random
from typing import Callable, Dict, List, Optional

from pydantic import BaseModel

from simulation.Component import Component, Chassis
from simulation.DroidComponents import Motivator
from simulation.Entity import Location
from simulation.GlobalConfig import GlobalConfig
from simulation.QueuedWebRequest import QueuedHttpRequest
from simulation.ToolCall import ToolCall, ToolCallResult, ToolCallState
from simulation.World import World

class AgentContext(BaseModel):
    """
    A context for the agent that contains the system prompt, tools, recent history, and world state.
    This is used to provide the agent with the necessary information to make decisions.
    """
    prompt_goal: str  # The goal of the agent, typically a prompt for the LLM
    prompt_system: Optional[str] = None  # The system prompt for the agent stating general instructions
    tools: List[ToolCall] = []  # List of tools available to the agent

    _recent_messages: List[Dict] = []  # Recent messages or history for the agent to consider

    def __init__(self,
                 prompt_goal: str,
                 prompt_system: Optional[str] = None,
                 # cache_prompt: bool = True, # TODO: Only used by llama.cpp
                 tools: Optional[List[ToolCall]] = None):
        super().__init__()
        self.prompt_goal = prompt_goal
        self.prompt_system = prompt_system
        # self.cache_prompt = cache_prompt  # TODO: Only used by llama.cpp
        self.tools = tools if tools is not None else []

    def to_json(self) -> Dict:
        messages:List[Dict] = []

        # If a system prompt is provided, append it as the first message
        if self.prompt_system:
            messages.append(dict(
                role="system", 
                content=self.prompt_system))

        # Append the goal as a user message            
        messages.append(dict(
            role="user", 
            content=self.prompt_goal))
        
        # Append the recent messages to the context
        # TODO: Limit the number of recent messages to avoid context overflow
        for message in self._recent_messages:
            messages.append(message)

        # Serialize tools to JSON
        tools_as_json = [tool.to_openai_json() for tool in self.tools]

        return dict(
                    messages=self.messages,
                    model="gpt-3.5-turbo",  # TODO: Make this configurable
                    tools=tools_as_json,
                    cache_prompt=True,      # TODO: Only used by llama.cpp
                    temperature=GlobalConfig.llm_temperature,
                    top_p=GlobalConfig.llm_top_p,
                    top_k=GlobalConfig.llm_top_k,
                    seed=GlobalConfig.llm_seed,
                )

    def append_message(self, role: str, content: str, tool_call_id: Optional[str] = None, tool_name: Optional[str] = None):
        """
        Append a message to the recent messages in the agent context.
        Args:
            role (str): The role of the message sender (e.g., "user", "assistant", "system").
            content (str): The content of the message.
        """
        if tool_call_id and tool_name:
            # If a tool call ID and name are provided, append a tool message
            self._recent_messages.append(dict(
                role=role,
                content=content,
                tool_call_id=tool_call_id,
                name=tool_name
            ))
        else:
            # Otherwise, append a regular message
            self._recent_messages.append(dict(role=role, content=content))


# A DroidAgent is a component that defines how a droid interacts with the world.
#  Specifically, it is an agent that can make decisions based on the world state.
#  Personalities can be simple / random, or can be controlled by more complex AI (such as an LLM)
class DroidAgent(Component):
    name: str = "Droid Agent"

    prompt_system: str = "You are a helpful droid. You will do your best to complete your tasks. You will use the tools provided to you to accomplish your tasks. You will not make assumptions about the state of the farm or the equipment, and you will only use the information provided to you in this conversation."
    prompt_goal: str = ""

    is_active: bool = False # Whether the agent is currently active / awake (and running its agentic loop)

    queued_http_request: Optional[QueuedHttpRequest] = None  # A queued web request that the agent can use to communicate with an LLM or other service
    pending_tool_call: Optional[ToolCall] = None  # A tool call that has started, but not yet completed.
    pending_tool_completion_callback: Optional[Callable[[], ToolCallResult]] = None  # A callback to call to check if the pending tool call has completed.
    pending_tool_call_id: Optional[str] = None  # The ID of the pending tool call, if any

    agent_context: Optional[AgentContext] = None  # The context for the agent, containing the system prompt, tools, and recent history

    def activate(self):
        # Initialize the agent with the provider and system prompt
        self.agent_context = AgentContext(
            prompt_goal=self.prompt_goal,
            prompt_system=self.prompt_system,
            tools=self.chassis.get_available_tools()  # Get the tools available in the chassis
        )
        self.info(f"Agent context initialized with system prompt: {self.agent_context.prompt_system}")
        self.is_active = True  # Set the agent to active state

    def tick(self):
        # A re-entrant ReAct agent "loop" that steps forward every tick
        if not self.is_active:
            # If the agent is not active, do nothing
            return

        world:World = self.chassis.world

        if self.queued_http_request:
            if self.queued_http_request.in_progress:
                # TODO: What's the best way to let the simulation know that the agent is thinking?
                # HACK: For now, set a flag on the world manually
                world.entity_thinking_count += 1
                self.info(f'Agent is thinking... (World thinking count: {world.entity_thinking_count})')
            else:
                # If the queued web request is done, we can process the response
                resp = self.queued_http_request.response
                self.info(f'Agent received response from web request: {resp}')
                self.queued_http_request = None

                assert len(resp["choices"]) > 0, "No choices in response from LLM API"
                # TODO: Turn the agent off and back on again to clear context and try again.

                choice = resp["choices"][0]
                content = choice["message"]["content"]

                if content:
                    self.info(f'Received response: {content}')
                    self.agent_context.append_message("assistant", content)  # Append the response to the agent context

                if choice["finish_reason"] == "tool_calls":
                    assert "tool_calls" in choice["message"], "No tool calls in response from LLM API"
                    self.info(f'Response contained {len(choice["message"]["tool_calls"])} tool calls.')

                    for tool_call in choice["message"]["tool_calls"]:
                        # For each tool call, execute it, and save the response to the agent context
                        tool_name = tool_call["function"]["name"]
                        tool_call_id = tool_call["id"]

                        params = tool_call["function"]["arguments"]
                        self.info(f'Executing tool call: {tool_name} with params: {params}')

                        tools = self.chassis.get_available_tools()

                        if tool_name in tools:
                            tool = tools[tool_name]
                            # Execute the tool call and get the response
                            try:
                                tool_response = tool.execute(params)
                                # If the tool_response is a function pointer, then we need to save it for later execution
                                # This is useful for tools that are asynchronous or require further processing
                                if callable(tool_response) and hasattr(tool_response, '__call__'):
                                    self.pending_tool_completion_callback = tool_response
                                    self.pending_tool_call = tool
                                    self.pending_tool_call_id = tool_call_id  # Save the ID of the pending tool call so that its results can be added later
                                    self.info(f'Tool call {tool_name} is executing and pending resolution.')
                            except Exception as e:
                                self.error(f'Error executing tool `{tool_name}`: {e}')
                                self.agent_context.append_message("error", f"Error executing tool `{tool_name}`: {e}", tool_call_id=tool_call_id, tool_name=tool_name)
                        else:
                            self.error(f'Tool call `{tool_name}` not found in available tools.')
                            self.agent_context.append_message("error", f"Tool call `{tool_name}` not found in available tools.", tool_call_id=tool_call_id, tool_name=tool_name)
                else:
                    # If the response does not contain tool calls, just append the content to the agent context
                    self.agent_context.append_message("assistant", content)
        elif self.pending_tool_call:
            # If there is a pending tool call, we need to check if it has completed
            # Attempt to get the tool call result from the pending tool call callback
            if not self.pending_tool_completion_callback:
                self.error(f'No pending tool completion callback for tool call `{self.pending_tool_call.function_ptr.__name__}`.')
            else:
                tool_call_result:ToolCallResult = self.pending_tool_completion_callback()
                if tool_call_result.state == ToolCallState.IN_PROGRESS:
                    # If the tool call is still in progress, do nothing for this tick
                    self.info(f'Tool call `{self.pending_tool_call.function_ptr.__name__}` is still in progress.')
                elif tool_call_result.state == ToolCallState.COMPLETED:
                    # If the tool call has completed, we can append the result to the agent context
                    self.agent_context.append_message("tool", f"{self.pending_tool_call.function_ptr.__name__} executed successfully: {tool_call_result.data}")
                    self.info(f'Tool call {self.pending_tool_call.function_ptr.__name__} executed successfully: {tool_call_result.data}')
                    self.pending_tool_call = None
                elif tool_call_result.state == ToolCallState.FAILED:
                    # If the tool call has failed, we can append the error message to the agent context
                    self.agent_context.append_message("error", f"Tool call `{self.pending_tool_call.function_ptr.__name__}` failed: {tool_call_result.message}")
                    self.error(f'Tool call {self.pending_tool_call.function_ptr.__name__} failed: {tool_call_result.message}')
                    self.pending_tool_call = None

        else:
            # No queued web request, so we can proceed with the next step in the agentic loop.
            # Append the current world state + query to the agent context and send it to the LLM
            self.agent_context.append_message("user", f"{world.get_state_llm()}: What is your next action?")  # Current world state with prompt for next action

            queued_web_request = QueuedHttpRequest(
                url=GlobalConfig.llm_api_url,
                data= self.agent_context.to_json(),
            )
            queued_web_request.begin_send(timeout=5.0)  # Send the request with a timeout of 5 seconds
            self.queued_http_request = queued_web_request

        # If there is no queued web request, then we should kick off the next step in the agentic loop


class DroidAgentRandom(DroidAgent):
    think_timer: int = 0  # Timer to control thinking intervals
    think_interval: int = 1  # Interval between thoughts in world ticks

    def tick(self):

        # Check to see if we are currently busy w/ an active task or tool call
        # If there is no active tool call, then we can perform one
        #if self.active_tool_call:
        #  print (f"Active tool call: {self.active_tool_call.function_ptr.__name__}")
        #else:
        #  print("No active tool call, performing random action.")
        #  TODO: Move to a random entity or location, charge something, etc.
        
        # For now, the only action is to move, but can code in more complex actions later
        
        # Find the motivator in the chassis
        motivator:Motivator = self.chassis.get_component(Motivator)

        if not motivator:
            self.error("Motivator component not found in chassis. Cannot move.")
            return
        
        # Only think about moving when not currently moving
        if motivator.destination is None:
            # Only think about moving when not currently moving
            self.think_interval += 1
            if self.think_timer >= self.think_interval:
                # We are done delaying, so now we can think about moving
                self.think_timer = 0.0
                self.think_interval = random.randint(1, 5) # Reset think interval

                dest = self.decide_movement()
                if dest:
                    motivator.move_to_location(dest.x, dest.y)

    def decide_movement(self) -> Location | None:
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
            return target_location
        
        return None

class DroidAgentSimple(DroidAgent):
    pass

class DroidAgentSimplePowerDroid(DroidAgentSimple):
    prompt_system:str = "You are an {model} {subtype}. Your name is '{name}'. Your ID is '{object_id}'. You use tools and functions to accomplish your daily tasks. Don't overthink things. Your purpose is to charge the batteries of equipment on the farm and ensure they are all supplied with power. You can recharge your own batteries at power stations to ensure you can carry enough power to charge the equipment. When everything is fully charged, and your own batteries are recharged, you can switch yourself off at the power station. You can move to specific locations or objects on the farm. You are a helpful and efficient droid, and you will do your best to complete your tasks. You will use the tools provided to you to accomplish your tasks. If you cannot complete a task, you will inform the user of the reason why. You will not make assumptions about the state of the farm or the equipment, and you will only use the information provided to you in this conversation."
