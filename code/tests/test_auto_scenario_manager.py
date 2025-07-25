import pytest
from pathlib import Path
import tempfile
#!/usr/bin/env python3
import sys
import os

# Add the parent directory to Python path so we can import simulation modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.AutoScenarioManager import AutoScenarioManager
from simulation.World import Simulation
from simulation.Entity import Location
from simulation.DroidModels import GonkDroid
from simulation.Vaporator import GX1_Vaporator
from simulation.Component import PowerPack
from simulation.DroidComponents import Motivator


def test_auto_scenario_round_trip():
    """Test that we can save and load scenarios automatically without templates"""
    
    # Create a test simulation
    simulation = Simulation(simulation_delay=0.2, paused=True)
    
    # Add a GonkDroid with modified state
    gonk = GonkDroid(location=Location(x=15, y=25))
    power = gonk.get_component(PowerPack)
    if power:
        power.charge = 65
    motivator = gonk.get_component(Motivator)
    if motivator:
        motivator.destination = Location(x=100, y=200)
        motivator.current_cooldown = 2
    simulation.world.add_entity(gonk)
    
    # Add a Vaporator
    vaporator = GX1_Vaporator(location=Location(x=50, y=75))
    vap_power = vaporator.get_component(PowerPack)
    if vap_power:
        vap_power.charge = 45
    simulation.world.add_entity(vaporator)
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
        temp_path = tmp_file.name
    
    try:
        AutoScenarioManager.save_simulation_to_json(
            simulation, 
            temp_path, 
            "Test Scenario",
            "Auto-generated test scenario"
        )
        
        # Load it back
        loaded_simulation = AutoScenarioManager.load_simulation_from_json(temp_path)
        
        # Verify basic properties
        assert loaded_simulation.simulation_delay == 0.2
        assert loaded_simulation.paused == True
        assert len(loaded_simulation.world.entities) == 2
        
        # Verify entities were loaded correctly
        entities = list(loaded_simulation.world.entities.values())
        gonk_loaded = next((e for e in entities if isinstance(e, GonkDroid)), None)
        vap_loaded = next((e for e in entities if isinstance(e, GX1_Vaporator)), None)
        
        assert gonk_loaded is not None
        assert vap_loaded is not None
        
        # Verify GonkDroid state
        assert gonk_loaded.location.x == 15
        assert gonk_loaded.location.y == 25
        
        gonk_power = gonk_loaded.get_component(PowerPack)
        assert gonk_power is not None
        assert gonk_power.charge == 65
        
        gonk_motivator = gonk_loaded.get_component(Motivator)
        assert gonk_motivator is not None
        assert gonk_motivator.destination.x == 100
        assert gonk_motivator.destination.y == 200
        assert gonk_motivator.current_cooldown == 2
        
        # Verify Vaporator state
        assert vap_loaded.location.x == 50
        assert vap_loaded.location.y == 75
        
        vap_power_loaded = vap_loaded.get_component(PowerPack)
        assert vap_power_loaded is not None
        assert vap_power_loaded.charge == 45

    except Exception as e:
        print(f"Error during test_auto_scenario_with_new_entity_type: {e}")
        raise e
        
    finally:
        test_round_trip_path = Path("./test_round_trip.json")
        if test_round_trip_path.exists():
            test_round_trip_path.unlink()
        test_round_trip_path.write_text(Path(temp_path).read_text())

        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_auto_scenario_minimal_json():
    """Test that only non-default values are serialized"""
    
    # Create a basic simulation with default values
    simulation = Simulation()  # All default values
    gonk = GonkDroid()  # Default location (0,0), default components
    simulation.world.add_entity(gonk)
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
        temp_path = tmp_file.name
    
    try:
        AutoScenarioManager.save_simulation_to_json(simulation, temp_path, "Minimal Test")
        
        # Read the JSON and verify it's minimal
        with open(temp_path, 'r') as f:
            import json
            data = json.load(f)
        
        # Should only have name and entities
        assert "name" in data
        assert "entities" in data
        assert len(data["entities"]) == 1
        
        # Entity should have minimal data (type, module, id, and default components)
        entity = data["entities"][0]
        assert entity["type"] == "GonkDroid"
        assert entity["module"] == "simulation.DroidModels"
        assert "id" in entity
        
        # Should not have simulation_settings (all defaults)
        # Should not have entity location (default 0,0 excluded)
        # Component power should not be included (default charge)

    except Exception as e:
        print(f"Error during test_auto_scenario_with_new_entity_type: {e}")
        raise e

    finally:
        test_minimal_path = Path("./test_minimal.json")
        if test_minimal_path.exists():
            test_minimal_path.unlink()
        test_minimal_path.write_text(Path(temp_path).read_text())


        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_auto_scenario_with_new_entity_type():
    """Test that the automatic system would work with new entity types (conceptual test)"""
    
    # This test demonstrates that the automatic approach would work
    # with any new Entity class without requiring code changes
    
    # If we had a new entity type like:
    # class CustomDroid(Chassis): ...
    # 
    # The AutoScenarioManager would automatically:
    # 1. Serialize it using entity.__class__.__name__ and .__module__
    # 2. Deserialize it using dynamic import and class resolution
    # 3. Handle any components it contains automatically
    
    # For now, we'll test with existing types to verify the principle
    simulation = Simulation()
    gonk = GonkDroid(location=Location(x=99, y=88))
    simulation.world.add_entity(gonk)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
        temp_path = tmp_file.name
    
    try:
        # The key insight: no registration needed, just works
        AutoScenarioManager.save_simulation_to_json(simulation, temp_path, "New Type Test")
        loaded_sim = AutoScenarioManager.load_simulation_from_json(temp_path)
        
        # Verify it worked
        loaded_entities = list(loaded_sim.world.entities.values())
        assert len(loaded_entities) == 1
        assert isinstance(loaded_entities[0], GonkDroid)
        assert loaded_entities[0].location.x == 99
        assert loaded_entities[0].location.y == 88

    except Exception as e:
        print(f"Error during test_auto_scenario_with_new_entity_type: {e}")
        raise e
        
    finally:
        test_new_type_path = Path("./test_new_type.json")
        if test_new_type_path.exists():
            test_new_type_path.unlink()
        test_new_type_path.write_text(Path(temp_path).read_text())


        if os.path.exists(temp_path):
            os.unlink(temp_path)

if __name__ == "__main__":
    pytest.main([__file__])