import json
import pytest
from simulation.Component import PowerPack
from simulation.DroidAgents import DroidAgent, DroidAgentSimplePowerDroid
from simulation.DroidComponents import Chronometer, Motivator
from simulation.QueuedWebRequest import QueuedHttpRequest
from simulation.ToolCall import ToolCall, ToolCallParameter
from simulation.World import Simulation, World
from simulation.DroidModels import GonkDroid
from simulation.Entity import Location

@pytest.fixture
def simulation() -> Simulation:
    """Fixture to create a simulation instance for testing."""    
    sim = Simulation(simulation_delay=0, web_server_enabled=False)
    return sim

def test_droid_movement(simulation: Simulation):
    droid = GonkDroid(location=Location(x=0, y=0))
    simulation.world.add_entity(droid)
    motivator = droid.get_component(Motivator)
    motivator.destination = Location(x=25, y=-25)

    print(f'Initial droid location: {droid.location.x}, {droid.location.y}')

    simulation.run_sync(ticks=100)  # Run the simulation for 50 ticks
    
    print(f'Final droid location: {droid.location.x}, {droid.location.y}')

    assert droid.location.x == 25
    assert droid.location.y == -25

# A droid with low power shouldn't be able to make it all the way to its destination
def test_droid_movement_low_battery(simulation: Simulation):
    droid = GonkDroid(location=Location(x=0, y=0))
    power: PowerPack = droid.get_component(PowerPack)
    power.charge = 10  # Start with low power
    simulation.world.add_entity(droid)

    motivator = droid.get_component(Motivator)
    motivator.destination = Location(x=25, y=-25)

    print(f'Initial droid location: {droid.location.x}, {droid.location.y}')
    print(f'Initial droid power: {power.charge}')
    simulation.run_sync(ticks=50)

    print(f'Final droid location: {droid.location.x}, {droid.location.y}')
    print(f'Final droid power: {power.charge}')

    assert droid.location.x < 25
    assert droid.location.y > -25
    assert power.charge < 10  # Should have used some power

def test_droid_agent_behavior_chronometer(simulation: Simulation):
    droid = GonkDroid(location=Location(x=0, y=0))
    # Add an agent brain to the droid in the correct slot
    agent = droid.slots["agent"].component
 
    # Add a chronometer to the droid to track time
    chronometer = Chronometer()
    droid.install_component("misc", chronometer)

    simulation.world.add_entity(droid)

    # Run one tick to initialize the event loop
    simulation.run_sync(ticks=1)

    request = QueuedHttpRequest(
        "http://example.com/api"
    )
    request.in_progress = False
    # Simulate the droid receiving a command to sleep for 5 ticks as the main choice
    request.response = {
        "choices": [
            {
                "finish_reason": "tool_calls",
                "message": {
                    "role": "assistant",
                    "content": "I will sleep for 5 ticks.",
                    "tool_calls": [
                        {
                            "id": "tool_call_1",
                            "function": {
                                "name": "sleep",
                                "arguments": json.dumps({"ticks": 5})
                            }
                        }
                    ]
                }
            }
        ]
    }
    agent.queued_http_request = request
    agent.activate() # Activate the agent to start processing

    # Assert that there is no pending tool call before running the simulation
    assert agent.pending_tool_call is None
    # Run the simulation for 1 tick to process the queued request
    simulation.run_sync(ticks=1)
    # Assert that the tool call was created and is pending
    assert agent.pending_tool_call is not None

    # Check that there is a pending tool call for sleeping
    assert agent.pending_tool_call.function_ptr.__name__ == "sleep"

    # Run the simulation for 5 ticks to allow the droid to sleep
    simulation.run_sync(ticks=5)

    # Check to see that there is no pending tool call after the sleep is done
    assert agent.pending_tool_call is None


def test_droid_agent_behavior(simulation: Simulation):
    droid = GonkDroid(location=Location(x=0, y=0))
    # Add an agent brain to the droid in the correct slot
    agent = droid.slots["agent"].component
 
    simulation.world.add_entity(droid)

    agent.activate("Go to location (10, -10)") # Activate the agent to start processing

    # Assert that there is a queued HTTP request
    assert agent.queued_http_request is not None

    # Run the simulation to process the queued request
    simulation.run_sync(ticks=50)

    # Assert that the droid has moved to the destination
    assert droid.location.x == 10
    assert droid.location.y == -10


