import pytest
from simulation.entity.component.Component import PowerPack
from simulation.World import Simulation, World
from simulation.entity.Vaporator import WaterTank, GX1_Vaporator, GX8_Vaporator
from simulation.entity.Entity import Location

@pytest.fixture
def simulation() -> Simulation:
    """Fixture to create a simulation instance for testing."""
    sim = Simulation(simulation_delay=0, web_server_enabled=False)
    return sim

def test_gx1_vaporator_full_tank(simulation: Simulation):
    vaporator = GX1_Vaporator()
    simulation.world.add_entity(vaporator)

    tank:WaterTank = vaporator.get_component(WaterTank)
    power:PowerPack = vaporator.get_component(PowerPack)

    assert tank.fill == 0  # Initial tank fill should be 0
    assert power.charge == power.charge_max  # Initial power pack charge should be full

    print(f'Initial tank fill: {tank.fill}, Initial power charge: {power.charge}')

    simulation.run_sync(ticks=100)  # Run the simulation for 100 ticks

    assert tank.fill == tank.capacity
    assert power.charge == 0

    print(f"Final tank fill: {tank.fill}, Final power charge: {power.charge}")

    #import json
    #world_json = simulation.world.to_json()
    ## Convert to valid JSON for Javascript
    #world_json_str = json.dumps(world_json, indent=2)
    #print(f"World JSON: {world_json_str}")

def test_gx1_vaporator_low_starting_power(simulation: Simulation):
    vaporator = GX1_Vaporator(location=Location(x=0, y=0))
    tank:WaterTank = vaporator.get_component(WaterTank)
    power:PowerPack = vaporator.get_component(PowerPack)   
    power.charge = 10  # Start with low power
    simulation.world.add_entity(vaporator)

    # Assert that we have low power and empty tank
    assert tank.fill == 0
    assert power.charge == 10

    print(f'Initial tank fill: {tank.fill}, Initial power charge: {power.charge}')

    simulation.run_sync(ticks=100)  # Run the simulation for 100 ticks

    tank = vaporator.get_component(WaterTank)
    assert tank.fill < tank.capacity
    assert power.charge == 0

    print(f"Final tank fill: {tank.fill}, Final power charge: {power.charge}")

def test_gx8_vaporator(simulation: Simulation):
    vaporator = GX8_Vaporator()
    simulation.world.add_entity(vaporator)

    tank: WaterTank = vaporator.get_component(WaterTank)
    power: PowerPack = vaporator.get_component(PowerPack)

    print(f'Initial tank fill: {tank.fill}, Initial power charge: {power.charge}')

    assert tank.fill == 0  # Initial tank fill should be 0
    assert power.charge == power.charge_max  # Initial power pack charge should be full

    simulation.run_sync(ticks=100)  # Run the simulation for 100 ticks

    print(f"Final tank fill: {tank.fill}, Final power charge: {power.charge}")

    assert tank.fill == tank.capacity
    assert power.charge == 0
