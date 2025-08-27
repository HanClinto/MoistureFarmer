import pytest
from simulation.GlobalConfig import GlobalConfig
from simulation.core.entity.component.PowerAdapter import HeavyDutyPowerAdapter
from simulation.core.entity.component.PowerPack import PowerPack
from simulation.core.entity.component.WaterTank import WaterTank
from simulation.core.entity.Entity import Location
from simulation.core.Simulation import Simulation
from simulation.equipment.DroidModels import GonkDroid
from simulation.equipment.PowerStationModels import (MicroFusionPowerStation,
                                                     SolarPowerStation)
from simulation.equipment.VaporatorModels import GX1_Vaporator
from simulation.llm.ToolCall import ToolCallState


@pytest.fixture
def simulation() -> Simulation:
    """Fixture to create a simulation instance for testing."""
    sim = Simulation(simulation_delay=0, web_server_enabled=False)
    # Set log level to reduce verbosity during tests
    GlobalConfig.log_print_level = 2
    return sim

def test_recharge_vaporator(simulation: Simulation):
    vaporator = GX1_Vaporator(location=Location(x=0, y=0))
    tank:WaterTank = vaporator.get_component(WaterTank)
    power:PowerPack = vaporator.get_component(PowerPack)   
    power.charge = 10  # Start with low power
    simulation.world.add_entity(vaporator)

    # Assert that we have low power and empty tank
    assert tank.fill == 0
    assert power.charge == 10

    print(f'Initial tank fill: {tank.fill}, Initial power charge: {power.charge}')

    # Create a power droid to recharge it, next to the vaporator
    droid = GonkDroid(location=Location(x=1, y=0))
    droid_power:PowerPack = droid.get_component(PowerPack)
    droid_adapter: HeavyDutyPowerAdapter = droid.get_component(HeavyDutyPowerAdapter)    
    simulation.world.add_entity(droid)
    
    # Instruct the droid to charge the vaporator
    droid_adapter.charge_other(vaporator.id)

    simulation.run_sync(ticks=100)  # Run the simulation for 100 ticks

    tank = vaporator.get_component(WaterTank)
    assert tank.fill == tank.capacity
    assert power.charge > 0

    assert droid_adapter.tool_result.state == ToolCallState.SUCCESS

    print(f"Final tank fill: {tank.fill}, Final power charge: {power.charge}")
    print(f'Final droid power charge: {droid_power.charge}')


def test_recharge_droid(simulation: Simulation):
    # Create a droid next to a fusion power station.
    # The fusion power station should be powerful enough to charge the droid without supply drooping.

    droid = GonkDroid(location=Location(x=0, y=0))
    simulation.world.add_entity(droid)

    power: PowerPack = droid.get_component(PowerPack)
    power.charge = 10  # The droid should start with low power.

    # Create a nuclear power station next to the droid.
    power_station = MicroFusionPowerStation(location=Location(x=0, y=1))
    simulation.world.add_entity(power_station)

    # The fusion station should start out with full charge.
    power_station_power: PowerPack = power_station.get_component(PowerPack)

    # Assign the droid to charge itself from the power station.
    droid_adapter: HeavyDutyPowerAdapter = droid.get_component(HeavyDutyPowerAdapter)
    droid_adapter.recharge_self(power_station.id)

    print(f'Initial droid charge: {power.charge}')
    print(f'Initial station charge: {power_station_power.charge}')

    simulation.run_sync(ticks=25)  # Run the simulation for a short time

    # The fusion station should be more than enough to charge a single droid without issue.
    assert power.charge == power.charge_max
    assert droid_adapter.tool_result.state == ToolCallState.SUCCESS

    print(f"Final power charge: {power.charge}")
    print(f'Final station charge: {power_station_power.charge}')


def test_recharge_droid_slow(simulation: Simulation):
    # Create a droid next to a solar power station.
    # The solar power station won't be able to charge the droid fast enough for its liking,
    # so we expect the droid to remain undercharged for a while.
    # Test that the droid does not quit, and waits patiently for the solar generator to charge it,
    # without failing the tool call.

    droid = GonkDroid(location=Location(x=0, y=0))
    simulation.world.add_entity(droid)

    power: PowerPack = droid.get_component(PowerPack)
    power.charge = 10  # The droid should start with low power.

    # Create a solar power station next to the droid.
    solar_station = SolarPowerStation(location=Location(x=0, y=1))
    simulation.world.add_entity(solar_station)

    # The solar station should start out with low charge as well.
    solar_station_power: PowerPack = solar_station.get_component(PowerPack)
    solar_station_power.charge = 50

    # Assign the droid to charge itself from the power station.
    droid_adapter: HeavyDutyPowerAdapter = droid.get_component(HeavyDutyPowerAdapter)
    droid_adapter.recharge_self(solar_station.id)

    print(f'Initial power charge: {power.charge}')

    simulation.run_sync(ticks=100)  # Run the simulation for 100 ticks

    assert power.charge < power.charge_max
    print(f'Partway through, and power charge is only up to {power.charge}')

    # Test that the droid does not quit, and waits patiently for the solar generator to charge it,
    # without failing the tool call.
    assert droid_adapter.tool_result.state == ToolCallState.IN_PROCESS

    # Run the simulation for some more ticks, and check the final power charge.
    simulation.run_sync(ticks=200)
    assert power.charge == power.charge_max
    assert droid_adapter.tool_result.state == ToolCallState.SUCCESS

    print(f"Final power charge: {power.charge}")
