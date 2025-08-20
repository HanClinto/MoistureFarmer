import pytest
import json
import tempfile
import os
from pathlib import Path

from simulation.ScenarioManager import (
    ScenarioManager, ScenarioTemplate, EntityTemplate, 
    save_simulation_as_scenario, load_scenario, create_test_scenarios
)
from simulation.World import Simulation
from simulation.Entity import Location
from simulation.DroidModels import GonkDroid
from simulation.Vaporator import GX1_Vaporator
from simulation.Component import PowerPack


def test_scenario_json_serialization():
    """Test that scenarios can be saved to and loaded from JSON"""
    
    # Create a test scenario
    scenario = ScenarioTemplate(
        name="Test Scenario",
        description="A simple test scenario",
        simulation_settings={
            "simulation_delay": 0.5,
            "tick_count": 0
        },
        entities=[
            EntityTemplate(
                type="GonkDroid",
                location=Location(x=10, y=20),
                component_overrides={
                    "power_pack": {
                        "charge": 75
                    }
                }
            ),
            EntityTemplate(
                type="GX1_Vaporator",
                location=Location(x=50, y=50),
                component_overrides={
                    "power_pack": {
                        "charge": 25
                    }
                }
            )
        ]
    )
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    try:
        ScenarioManager.save_scenario_to_json(scenario, temp_path)
        
        # Load it back
        loaded_scenario = ScenarioManager.load_scenario_from_json(temp_path)
        
        # Verify it matches
        assert loaded_scenario.name == scenario.name
        assert loaded_scenario.description == scenario.description
        assert loaded_scenario.simulation_settings == scenario.simulation_settings
        assert len(loaded_scenario.entities) == 2
        
        # Check first entity
        entity1 = loaded_scenario.entities[0]
        assert entity1.type == "GonkDroid"
        assert entity1.location.x == 10
        assert entity1.location.y == 20
        assert entity1.component_overrides["power_pack"]["charge"] == 75
        
        # Check the JSON is minimal (excludes defaults)
        with open(temp_path, 'r') as f:
            json_data = json.load(f)
        
        print("Generated JSON:")
        print(json.dumps(json_data, indent=2))
        
        # Verify JSON structure is clean
        assert "name" in json_data
        assert "entities" in json_data
        # Should not have empty/default fields
        
    finally:
        os.unlink(temp_path)


def test_scenario_to_simulation():
    """Test loading a scenario into a simulation"""
    
    scenario = ScenarioTemplate(
        name="Power Test",
        simulation_settings={
            "simulation_delay": 0.1
        },
        entities=[
            EntityTemplate(
                type="GonkDroid",
                location=Location(x=0, y=0),
                component_overrides={
                    "power_pack": {
                        "charge": 30
                    }
                }
            )
        ]
    )
    
    # Load into simulation
    simulation = ScenarioManager.load_scenario_into_simulation(scenario)
    
    # Verify simulation settings
    assert simulation.simulation_delay == 0.1
    
    # Verify entities
    assert len(simulation.world.entities) == 1
    
    droid = list(simulation.world.entities.values())[0]
    assert isinstance(droid, GonkDroid)
    assert droid.location.x == 0
    assert droid.location.y == 0
    
    power_pack = droid.get_component(PowerPack)
    assert power_pack.charge == 30


def test_create_scenario_from_simulation():
    """Test extracting a scenario from an existing simulation"""
    
    # Create a simulation with some entities
    simulation = Simulation(simulation_delay=0.5)
    
    # Add a droid with modified power
    droid = GonkDroid(location=Location(x=15, y=25))
    power_pack = droid.get_component(PowerPack)
    power_pack.charge = 42
    simulation.world.add_entity(droid)
    
    # Add a vaporator
    vaporator = GX1_Vaporator(location=Location(x=100, y=200))
    simulation.world.add_entity(vaporator)
    
    # Extract scenario
    scenario = ScenarioManager.create_scenario_from_simulation(
        simulation, 
        "Extracted Test", 
        "Generated from simulation"
    )
    
    # Verify scenario
    assert scenario.name == "Extracted Test"
    assert scenario.description == "Generated from simulation"
    assert scenario.simulation_settings["simulation_delay"] == 0.5
    assert len(scenario.entities) == 2
    
    # Check droid entity
    droid_template = next(e for e in scenario.entities if e.type == "GonkDroid")
    assert droid_template.location.x == 15
    assert droid_template.location.y == 25
    assert droid_template.component_overrides["power_pack"]["charge"] == 42
    
    # Check vaporator entity
    vap_template = next(e for e in scenario.entities if e.type == "GX1_Vaporator")
    assert vap_template.location.x == 100
    assert vap_template.location.y == 200


def test_predefined_scenarios():
    """Test the predefined test scenarios"""
    
    scenarios = create_test_scenarios()
    assert len(scenarios) == 3
    
    # Test droid movement scenario
    droid_scenario = scenarios[0]
    assert droid_scenario.name == "Droid Movement Test"
    
    simulation = ScenarioManager.load_scenario_into_simulation(droid_scenario)
    assert len(simulation.world.entities) == 1
    
    droid = list(simulation.world.entities.values())[0]
    assert isinstance(droid, GonkDroid)
    assert droid.location.x == 0
    assert droid.location.y == 0


def test_save_and_load_convenience_functions():
    """Test the convenience functions"""
    
    # Create a simple simulation
    simulation = Simulation()
    droid = GonkDroid(location=Location(x=5, y=10))
    simulation.world.add_entity(droid)
    
    # Save using convenience function
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    try:
        save_simulation_as_scenario(
            simulation, 
            "Convenience Test", 
            temp_path, 
            "Testing convenience functions"
        )
        
        # Load using convenience function
        loaded_simulation = load_scenario(temp_path)
        
        # Verify
        assert len(loaded_simulation.world.entities) == 1
        loaded_droid = list(loaded_simulation.world.entities.values())[0]
        assert loaded_droid.location.x == 5
        assert loaded_droid.location.y == 10
        
    finally:
        os.unlink(temp_path)
