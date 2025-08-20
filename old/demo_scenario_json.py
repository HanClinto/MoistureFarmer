#!/usr/bin/env python3
"""
Demonstration of Pydantic JSON serialization with minimal output for Moisture Farmer scenarios.

This script shows how the ScenarioManager uses Pydantic to create clean, minimal JSON
that excludes default values, making scenarios easy to read and edit.
"""

import json
from pathlib import Path
import sys
import os

# Add the code directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from simulation.ScenarioManager import (
    ScenarioManager, ScenarioTemplate, EntityTemplate, create_test_scenarios
)
from simulation.Entity import Location
from simulation.DroidModels import GonkDroid
from simulation.World import Simulation


def demonstrate_minimal_json():
    """Show how Pydantic creates minimal JSON output."""
    
    print("=== Moisture Farmer Scenario JSON Demonstration ===\n")
    
    # 1. Create a basic scenario with minimal data
    print("1. Basic scenario with defaults excluded:")
    basic_scenario = ScenarioTemplate(
        name="Basic Test",
        entities=[
            EntityTemplate(
                type="GonkDroid",
                location=Location(x=10, y=10)
                # No properties or component_overrides = excluded from JSON
            )
        ]
        # No description = excluded from JSON  
        # No simulation_settings = excluded from JSON
    )
    
    basic_json = basic_scenario.model_dump_json(exclude_defaults=True, exclude_none=True, indent=2)
    print(basic_json)
    print()
    
    # 2. Create a scenario with custom settings to show the difference
    print("2. Scenario with custom settings:")
    custom_scenario = ScenarioTemplate(
        name="Custom Test",
        description="Testing with custom values",
        simulation_settings={
            "simulation_delay": 0.5,  # Non-default value
            "paused": True            # Non-default value
        },
        entities=[
            EntityTemplate(
                type="GonkDroid",
                location=Location(x=25, y=50),
                component_overrides={
                    "power_pack": {
                        "charge": 75  # Non-default power level
                    },
                    "motivator": {
                        "destination": {"x": 100, "y": 100}
                    }
                }
            )
        ]
    )
    
    custom_json = custom_scenario.model_dump_json(exclude_defaults=True, exclude_none=True, indent=2)
    print(custom_json)
    print()
    
    # 3. Show how extraction from simulation works
    print("3. Extracting scenario from running simulation:")
    
    # Create a simulation with entities
    simulation = Simulation(simulation_delay=0.2, paused=True)  # Non-default values
    
    # Add a Gonk droid with modified power
    gonk = GonkDroid(location=Location(x=30, y=40))
    power_pack = gonk.get_component("power_pack")
    if power_pack:
        power_pack.charge = 60  # Modify from default
    simulation.world.add_entity(gonk)
    
    # Extract scenario from simulation
    extracted_scenario = ScenarioManager.create_scenario_from_simulation(
        simulation, 
        "Extracted Scenario",
        "Scenario extracted from running simulation"
    )
    
    extracted_json = extracted_scenario.model_dump_json(exclude_defaults=True, exclude_none=True, indent=2)
    print(extracted_json)
    print()
    
    # 4. Show predefined test scenarios
    print("4. Predefined test scenarios:")
    test_scenarios = create_test_scenarios()
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"--- Test Scenario {i}: {scenario.name} ---")
        scenario_json = scenario.model_dump_json(exclude_defaults=True, exclude_none=True, indent=2)
        print(scenario_json)
        print()
    
    # 5. Demonstrate save/load cycle
    print("5. Save/Load demonstration:")
    
    # Save to temporary file
    temp_path = Path("temp_scenario.json")
    try:
        ScenarioManager.save_scenario_to_json(custom_scenario, str(temp_path))
        print(f"Saved scenario to {temp_path}")
        
        # Show the actual file contents
        with open(temp_path, 'r') as f:
            file_contents = f.read()
        print("File contents:")
        print(file_contents)
        
        # Load it back
        loaded_scenario = ScenarioManager.load_scenario_from_json(str(temp_path))
        print(f"Loaded scenario: {loaded_scenario.name}")
        print(f"Entities: {len(loaded_scenario.entities)}")
        
    finally:
        # Cleanup
        if temp_path.exists():
            temp_path.unlink()
    
    print("\n=== Demonstration complete ===")


if __name__ == "__main__":
    demonstrate_minimal_json()
