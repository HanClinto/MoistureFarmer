import asyncio
import random
from typing import Dict, List, Optional

from pydantic import BaseModel

from simulation.Component import Component
from simulation.DroidComponents import Motivator
from simulation.Entity import Location
from simulation.QueuedWebRequest import QueuedWebRequest
from simulation.ToolCall import ToolCall
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
        for message in self._recent_messages:
            messages.append(message)

        # Serialize tools to JSON
        tools_as_json = [tool.to_openai_json() for tool in self.tools]

        return dict(
                    messages=self.messages,
                    model="gpt-3.5-turbo",  # TODO: Make this configurable
                    tools=tools_as_json,
                    cache_prompt=True,      # TODO: Only used by llama.cpp
                    # TODO: Make all of these configurable
                    #temperature=temperature,
                    #top_p=top_p,
                    #top_k=top_k,
                    #seed=seed,
                )

    def append_message(self, role: str, content: str):
        """
        Append a message to the recent messages in the agent context.
        Args:
            role (str): The role of the message sender (e.g., "user", "assistant", "system").
            content (str): The content of the message.
        """
        self._recent_messages.append(dict(role=role, content=content))
        # TODO: Optionally limit the size of recent messages to avoid memory overflow
        #if len(self._recent_messages) > 10: # TODO: Configurable threshold
        #    self._recent_messages.pop(0)



# A DroidAgent is a component that defines how a droid interacts with the world.
#  Specifically, it is an agent that can make decisions based on the world state.
#  Personalities can be simple / random, or can be controlled by more complex AI (such as an LLM)
class DroidAgent(Component):
    name: str = "Droid Agent"
    description: str = "You are an {model} {subtype}. Your name is '{name}'. Your ID is '{object_id}'. You use tools and functions to accomplish your daily tasks. Don't overthink things. Your purpose is to charge the batteries of equipment on the farm and ensure they are all supplied with power. You can recharge your own batteries at power stations to ensure you can carry enough power to charge the equipment. When everything is fully charged, and your own batteries are recharged, you can switch yourself off at the power station. You can move to specific locations or objects on the farm. You are a helpful and efficient droid, and you will do your best to complete your tasks. You will use the tools provided to you to accomplish your tasks. If you cannot complete a task, you will inform the user of the reason why. You will not make assumptions about the state of the farm or the equipment, and you will only use the information provided to you in this conversation."

    prompt_goal: str 

    is_active: bool = False # Whether the agent is currently active / awake (and running its agentic loop)

    queued_web_request: Optional[QueuedWebRequest] = None  # A queued web request that the agent can use to communicate with an LLM or other service

    agent_context: Optional[AgentContext] = None  # The context for the agent, containing the system prompt, tools, and recent history

    def on_activate(self):
        # Initialize the agent with the provider and system prompt

        # Activate the agent
        self.activate()

    def tick(self):
        # A re-entrant ReAct agent "loop" that steps forward every tick
        if not self.is_active:
            # If the agent is not active, do nothing
            return

        world:World = self.chassis.world

        if self.queued_web_request:
            if self.queued_web_request.in_progress:
                # TODO: What's the best way to let the simulation know that the agent is thinking?
                # HACK: For now, set a flag on the world manually
                world.entity_thinking_count += 1
                print(f'Still thinking...')
            else:
                # If the queued web request is done, we can process the response
                resp = self.queued_web_request.response
                print(f'Processing response: {resp}')
                self.queued_web_request = None
                # For each tool call, execute it, and save the response to the agent context
                # TODO: ^^
                # handle_tool_calls(resp)
                # For now, we will just print the response
                print(f'Agent response: {resp}')
        else:
            # No queued web request, so we can proceed with the next step in the agentic loop.
            # Append the current world state + query to the agent context and send it to the LLM
            self.agent_context.append(f"{world.get_state()}: What is your next action?")  # Current world state with prompt for next action

            queued_web_request = QueuedWebRequest(
                url=world.simulation.llm_url,  # Replace with actual LLM endpoint
                data={
                    "prompt": "\n".join(self.agent_context),  # Join the context into a single prompt
                    "tools": [tool.to_llm_json() for tool in self.provides_tools().values],  # Serialize tools to JSON
                }
            )
            queued_web_request.begin_send(timeout=5.0)  # Send the request with a timeout of 5 seconds
            self.queued_web_request = queued_web_request

        # If there is no queued web request, then we should kick off the next step in the agentic loop

    def activate(self):
        self.is_active = True
        # Initialize the agent context with the system prompt, tools, and recent history


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
            self.chassis.log_error("No Motivator component found in the chassis. Cannot move.")
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
    pass


