import pytest
from simulation.Component import PowerPack
from simulation.World import World
from simulation.Vaporator import WaterTank, GX1_Vaporator, GX8_Vaporator
from simulation.Entity import Location

@pytest.fixture
def world():
    return World()

def test_gx1_vaporator_full_tank(world):
    vaporator = GX1_Vaporator()
    world.add_entity(vaporator)

    tank:WaterTank = vaporator.get_component(WaterTank)
    power:PowerPack = vaporator.get_component(PowerPack)

    assert tank.fill == 0  # Initial tank fill should be 0
    assert power.charge == power.charge_max  # Initial power pack charge should be full

    print(f'Initial tank fill: {tank.fill}, Initial power charge: {power.charge}')

    for _ in range(100):
        world.tick()

    assert tank.fill == tank.capacity
    assert power.charge == 0

    print(f"Final tank fill: {tank.fill}, Final power charge: {power.charge}")

def test_gx1_vaporator_low_starting_power(world):
    vaporator = GX1_Vaporator(location=Location(x=0, y=0))
    tank:WaterTank = vaporator.get_component(WaterTank)
    power:PowerPack = vaporator.get_component(PowerPack)   
    power.charge = 10  # Start with low power
    world.add_entity(vaporator)

    # Assert that we have low power and empty tank
    assert tank.fill == 0
    assert power.charge == 10

    print(f'Initial tank fill: {tank.fill}, Initial power charge: {power.charge}')

    for _ in range(100):
        world.tick()

    tank = vaporator.get_component(WaterTank)
    assert tank.fill < tank.capacity
    assert power.charge == 0

    print(f"Final tank fill: {tank.fill}, Final power charge: {power.charge}")

def test_gx8_vaporator(world):
    vaporator = GX8_Vaporator()
    world.add_entity(vaporator)

    tank: WaterTank = vaporator.get_component(WaterTank)
    power: PowerPack = vaporator.get_component(PowerPack)

    print(f'Initial tank fill: {tank.fill}, Initial power charge: {power.charge}')

    assert tank.fill == 0  # Initial tank fill should be 0
    assert power.charge == power.charge_max  # Initial power pack charge should be full

    for _ in range(100):
        world.tick()

    print(f"Final tank fill: {tank.fill}, Final power charge: {power.charge}")

    assert tank.fill == tank.capacity
    assert power.charge == 0
