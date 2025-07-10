import asyncio
import random
from typing import List, Optional

from simulation.Component import Component
from simulation.DroidComponents import Motivator
from simulation.Entity import Location
from simulation.QueuedWebRequest import QueuedWebRequest
from simulation.World import World

# Import the LlamaCppServerProvider of llama-cpp-agent
from llama_cpp_agent import LlamaCppAgent
from llama_cpp_agent.providers import LlamaCppServerProvider
from llama_cpp_agent import MessagesFormatterType


# Create the provider by passing the server URL to the LlamaCppServerProvider class, you can also pass an API key for authentication and a flag to use a llama-cpp-python server.
provider = LlamaCppServerProvider("http://127.0.0.1:8080")

# A DroidAgent is a component that defines how a droid interacts with the world.
#  Specifically, it is an agent that can make decisions based on the world state.
#  Personalities can be simple / random, or can be controlled by more complex AI (such as an LLM)
class DroidAgent(Component):
    name: str = "Droid Agent"
    description: str = "A simple droid agent that can make decisions based on the world state."

    is_active: bool = False # Whether the agent is currently active / awake (and running its agentic loop)

    queued_web_request: Optional[QueuedWebRequest] = None  # A queued web request that the agent can use to communicate with an LLM or other service

    #agent: LlamaCppAgent = None

    def on_activate(self):
        # Initialize the agent with the provider and system prompt
        #self.agent = LlamaCppAgent(
        #    provider=provider,
        #    system_prompt=self.system_prompt,
        #    tools=self.provides_tools(),
        #    recent_history=self.recent_history,
        #    predefined_messages_formatter_type=MessagesFormatterType.CHATML
        #)

        self.chassis

        # Activate the agent
        self.activate()

    def tick(self):
        # A re-entrant ReAct agent "loop" that steps forward every tick
        if not self.is_active:
            # If the agent is not active, do nothing
            return

        world = self.chassis.world

        if self.queued_web_request:
            if self.queued_web_request.in_progress:
                # TODO: What's the best way to let the simulation know that the agent is thinking?
                # HACK: For now, set a flag on the world manually
                world.simulation.entity_thinking_count += 1
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

        world = self.chassis.world

        # Build the initial context for the agent
        self.agent_context = []
        self.agent_context.append(self.system_prompt)  # System prompt
        self.agent_context.append(self.provides_tools())  # Tool calls available to the agent
        self.agent_context.append(self.recent_history)  # Recent history of actions
        self.agent_context.append(f"{world.get_state()}: What is your next action?")  # Current world state with prompt for next action


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


