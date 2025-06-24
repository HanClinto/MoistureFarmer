import pytest
from simulation.Component import PowerPack
from simulation.World import World
from simulation.DroidModels import GonkDroid
from simulation.Entity import Location

@pytest.fixture
def world():
    return World()

def test_droid_movement(world):
    droid = GonkDroid(location=Location(x=0, y=0))
    world.add_entity(droid)
    droid.destination = Location(x=25, y=-25)

    print(f'Initial droid location: {droid.location.x}, {droid.location.y}')

    for _ in range(50):
        world.tick()
    
    print(f'Final droid location: {droid.location.x}, {droid.location.y}')

    assert droid.location.x == 25
    assert droid.location.y == -25

def test_droid_movement_low_battery(world):
    droid = GonkDroid(location=Location(x=0, y=0))
    power: PowerPack = droid.get_component(PowerPack)
    power.charge = 10  # Start with low power
    world.add_entity(droid)

    droid.destination = Location(x=25, y=-25)

    print(f'Initial droid location: {droid.location.x}, {droid.location.y}')
    print(f'Initial droid power: {power.charge}')
    for _ in range(50):
        world.tick()

    print(f'Final droid location: {droid.location.x}, {droid.location.y}')
    print(f'Final droid power: {power.charge}')

    assert droid.location.x < 25
    assert droid.location.y > -25
    assert power.charge < 10  # Should have used some power