import pytest
from simulation.Component import PowerPack
from simulation.DroidComponents import Motivator
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