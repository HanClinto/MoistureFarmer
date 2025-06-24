import pytest
from simulation.Component import PowerPack
from simulation.World import World
from simulation.Vaporator import WaterTank, Vaporator
from simulation.Droid import GonkDroid
from simulation.Entity import Location

@pytest.fixture
def world():
    return World()

def test_gx1_vaporator_full_tank(world):
    vaporator = Vaporator()
    world.add_entity(vaporator)

    tank:WaterTank = vaporator.get_component(WaterTank)
    power:PowerPack = vaporator.get_component(PowerPack)

    assert tank.fill == 0  # Initial tank fill should be 0
    assert power.charge == power.charge_max  # Initial power pack charge should be full

    for _ in range(100):
        world.tick()

    assert tank.fill == tank.capacity
    assert power.charge == 0

def test_gx1_vaporator_low_starting_power(world):
    vaporator = Vaporator(location=Location(x=0, y=0))
    tank:WaterTank = vaporator.get_component(WaterTank)
    power:PowerPack = vaporator.get_component(PowerPack)   
    power.charge = 10  # Start with low power
    world.add_entity(vaporator)

    # Assert that we have low power and empty tank
    assert tank.fill == 0
    assert power.charge == 10

    for _ in range(100):
        world.tick()

    tank = vaporator.get_component(WaterTank)
    assert tank.fill < tank.capacity
    assert power.charge == 0

"""
def test_gx1_vaporator_with_gonk_droid(world):
    vaporator = Vaporator(id="vaporator3", location=Location(x=0, y=0))
    power = vaporator.get_component(PowerPack)
    power.charge = 5  # Start with low power
    gonk = GonkDroid(id="gonk1", location=Location(x=1, y=0))
    # Stub: Gonk recharges vaporator's power pack each tick if not full
    def gonk_tick(world):
        vaporator_power = vaporator.get_component(PowerPack)
        if vaporator_power.charge < vaporator_power.__class__.charge:
            vaporator_power.charge += 1
    gonk.tick = gonk_tick
    world.add_entity(vaporator)
    world.add_entity(gonk)
    for _ in range(100):
        world.tick()
    tank = vaporator.get_component(WaterTank)
    assert tank.fill == tank.capacity
    assert power.charge > 0
"""