"""
Automatic Scenario Manager - No Templates Required!

This version uses Python introspection and Pydantic's built-in capabilities
to automatically handle any Entity or Component types without explicit registration.
"""

import json
import importlib
from typing import Dict, Any, Type, Optional

from simulation.core.entity.Entity import Entity, GameObject, Location
from simulation.core.Simulation import Simulation

# BEGIN REBUILD HACK: Rebuild models for a bunch of things so that we don't get circular referrence or import errors.
from simulation.core.entity.ComponentSlot import ComponentSlot
from simulation.core.entity.component.Component import Component
from simulation.core.entity.component.Motivator import Motivator
from simulation.core.entity.component.PowerPack import LargePowerPack, PowerPack, SmallPowerPack
from simulation.core.entity.Chassis import Chassis

Motivator.model_rebuild()
PowerPack.model_rebuild()
SmallPowerPack.model_rebuild()
LargePowerPack.model_rebuild()
Chassis.model_rebuild()
ComponentSlot.model_rebuild()
# END REBUILD HACK
class AutoScenarioManager:
    """Automatic scenario manager that discovers entity types dynamically"""
    
    @classmethod
    def save_simulation_to_json(cls, simulation: Simulation, file_path: str, name: str = None, description: str = None) -> None:
        """Save a simulation directly to JSON with automatic type discovery"""
        scenario_data = cls._simulation_to_dict(simulation, name, description)
        
        with open(file_path, 'w') as f:
            json.dump(scenario_data, f, indent=2)
    
    @classmethod
    def load_simulation_from_json(cls, file_path: str) -> Simulation:
        """Load a simulation directly from JSON with automatic type resolution"""
        with open(file_path, 'r') as f:
            scenario_data = json.load(f)
        
        return cls._dict_to_simulation(scenario_data)
    
    @classmethod
    def _simulation_to_dict(cls, simulation: Simulation, name: str = None, description: str = None) -> Dict[str, Any]:
        """Convert simulation to dictionary with minimal data"""
        result = {}
        
        # Add metadata if provided
        if name:
            result["name"] = name
        if description:
            result["description"] = description
        
        # Get simulation settings (excluding defaults and problematic fields)
        sim_settings = simulation.model_dump(
            exclude_defaults=True,
            exclude_none=True,
            exclude={'world', '_on_tick_subscribers', '__instance'}
        )
        if sim_settings:
            result["simulation_settings"] = sim_settings
        
        # Process entities
        entities = []
        for entity in simulation.world.entities.values():
            entity_data = cls._entity_to_dict(entity)
            if entity_data:  # Only add if there's meaningful data
                entities.append(entity_data)
        
        if entities:
            result["entities"] = entities
        
        return result
    
    @classmethod
    def _entity_to_dict(cls, entity: Entity) -> Dict[str, Any]:
        """Convert entity to dictionary with type information"""
        # Start with the entity type and module for automatic resolution
        entity_data = {
            "type": entity.__class__.__name__,
        }
        
        # Get entity properties (excluding defaults and circular references)
        props = entity.model_dump(
            exclude_defaults=True,
            exclude_none=True,
            exclude={'world', 'slots'}  # Exclude problematic fields
        )
        
        # Merge non-default properties
        entity_data.update(props)
        
        # Handle components if entity has slots
        if hasattr(entity, 'slots'):
            components = {}
            for slot_name, slot in entity.slots.items():
                if slot.component:
                    comp_data = cls._component_to_dict(slot)
                    if comp_data:  # Only include if there are non-default values
                        components[slot_name] = comp_data
            
            if components:
                entity_data["components"] = components
        
        return entity_data
    
    @classmethod
    def _component_to_dict(cls, slot:ComponentSlot) -> Optional[Dict[str, Any]]:
        """Convert component to dictionary"""
        try:
            component = slot.component

            comp_data = {
            }

            # Only include the component type information if it is not the default for the slot.
            component_type = component.__class__.__name__
            if not slot.default_component or slot.default_component.__name__ != component_type:
                print(f"Component in slot {slot.slot_id} is of type {component_type}, which differs from slot default {slot.accepts.__name__}")
                comp_data["type"] = component_type

            # Get component properties (excluding defaults and circular references)
            props = component.model_dump(
                exclude_defaults=True,
                exclude_none=True,
                exclude={'chassis', 'world', 'entity'}  # Exclude back-references
            )
            
            # Only return if there are meaningful properties beyond type info
            if props:
                comp_data.update(props)
                return comp_data
            elif comp_data["type"] != "Component":  # Include specific component types even without props
                return comp_data
            
        except ValueError as e:
            if "Circular reference" in str(e):
                print(f"Warning: Skipping component {component.__class__.__name__} due to circular reference")
            else:
                raise
        
        return None
    
    @classmethod
    def _dict_to_simulation(cls, scenario_data: Dict[str, Any]) -> Simulation:
        """Convert dictionary back to simulation"""
        # Create simulation with settings
        sim_settings = scenario_data.get("simulation_settings", {})
        # For each setting in sim_settings, set it on the Simulation instance
        simulation = Simulation.get_instance()
        simulation.tick_count = 0 # Reset tick count on load
        for key, value in sim_settings.items():
            if hasattr(simulation, key):
                setattr(simulation, key, value)
        
        # Clear entities from the old world
        simulation.world.clear_entities()
        print(f'*** Cleared old entities from the world ***')
        # Create entities
        for entity_data in scenario_data.get("entities", []):
            print(f'*** Creating entity from data: {entity_data} ***')
            entity = cls._dict_to_entity(entity_data)
            if entity:
                simulation.world.add_entity(entity)
                print(f'*** Added entity {entity.id} of type {entity.__class__.__name__} to the world ***')
            else:
                print(f'*** Warning: Could not create entity from data: {entity_data} ***')

        # Finalize world state
        print(f'*** Added {len(simulation.world.entities)} entities to the world ***')
        
        return simulation
    
    @classmethod
    def _dict_to_entity(cls, entity_data: Dict[str, Any]) -> Optional[Entity]:
        """Convert dictionary back to entity"""
        # Get the entity class dynamically
        entity_class = cls._resolve_class(entity_data["type"], entity_data.get("module"))
        if not entity_class:
            print(f"Warning: Could not resolve entity type {entity_data['type']}")
            return None
        
        # Prepare constructor arguments
        constructor_args = {}
        components_data = entity_data.pop("components", {})
        entity_type = entity_data.pop("type")
        entity_module = entity_data.pop("module", None)
        
        # Add remaining properties as constructor arguments
        constructor_args.update(entity_data)
        
        # Create the entity
        entity = entity_class(**constructor_args)
        
        # Apply component modifications
        if hasattr(entity, 'slots') and components_data:
            for slot_name, comp_data in components_data.items():
                if slot_name in entity.slots and entity.slots[slot_name].component:
                    cls._apply_component_data(entity.slots[slot_name].component, comp_data)
        
        return entity
    
    @classmethod
    def _apply_component_data(cls, component, comp_data: Dict[str, Any]):
        """Apply data to an existing component"""
        # Remove type/module info since we're modifying existing component
        comp_data = comp_data.copy()
        comp_data.pop("type", None)
        comp_data.pop("module", None)
        
        # Apply remaining properties
        for key, value in comp_data.items():
            if hasattr(component, key):
                # Handle special cases like Location objects
                if key == "location" and isinstance(value, dict):
                    setattr(component, key, Location(**value))
                elif key == "destination" and isinstance(value, dict):
                    setattr(component, key, Location(**value))
                else:
                    setattr(component, key, value)
    
    @classmethod
    def _resolve_class(cls, class_name: str, module_name: str = None) -> Optional[Type]:
        """Dynamically resolve a class by name and module"""
        try:
            # First, search for all subclasses of GameObject registered in the application and look for a match.
            game_object_classes = GameObject.__subclasses__()
            for cls in game_object_classes:
                if cls.__name__ == class_name:
                    return cls
                
            if module_name:
                # Try to import the specific module
                module = importlib.import_module(module_name)
                return getattr(module, class_name, None)
            else:
                # Fallback: search common simulation modules
                search_modules = [
                    "simulation.equipment.DroidModels",
                    "simulation.equipment.VaporatorModels",
                    "simulation.core.entity.Entity",
                    "simulation.core.entity.Component"
                ]
                
                for mod_name in search_modules:
                    try:
                        module = importlib.import_module(mod_name)
                        if hasattr(module, class_name):
                            return getattr(module, class_name)
                    except ImportError:
                        continue
        except Exception as e:
            print(f"Error resolving class {class_name}: {e}")
        
        return None


# Convenience functions with same interface as original
def save_simulation_as_scenario(simulation: Simulation, name: str, file_path: str, description: str = None):
    """Save current simulation state as a scenario using automatic manager"""
    AutoScenarioManager.save_simulation_to_json(simulation, file_path, name, description)


def load_scenario(file_path: str) -> Simulation:
    """Load a scenario and return a configured simulation using automatic manager"""
    return AutoScenarioManager.load_simulation_from_json(file_path)


def demo_automatic_scenarios():
    """Create test scenarios automatically without templates"""
    from simulation.equipment.DroidModels import GonkDroid
    from simulation.equipment.VaporatorModels import GX1_Vaporator
    from simulation.core.entity.component.PowerPack import PowerPack
    from simulation.core.entity.component.Motivator import Motivator
    
    scenarios = []
    
    # Scenario 1: Droid Movement (created programmatically)
    sim1 = Simulation(simulation_delay=0)
    gonk = GonkDroid(location=Location(x=0, y=0))
    motivator = gonk.get_component(Motivator)
    if motivator:
        motivator.destination = Location(x=25, y=-25)
    sim1.world.add_entity(gonk)
    scenarios.append(("Droid Movement Test", sim1))
    
    # Scenario 2: Low Battery Droid
    sim2 = Simulation(simulation_delay=0) 
    gonk2 = GonkDroid(location=Location(x=0, y=0))
    power = gonk2.get_component(PowerPack)
    if power:
        power.charge = 10
    motivator2 = gonk2.get_component(Motivator)
    if motivator2:
        motivator2.destination = Location(x=25, y=-25)
    sim2.world.add_entity(gonk2)
    scenarios.append(("Low Battery Droid Test", sim2))
    
    # Scenario 3: Vaporator
    sim3 = Simulation(simulation_delay=0)
    vaporator = GX1_Vaporator(location=Location(x=0, y=0))
    vap_power = vaporator.get_component(PowerPack)
    if vap_power:
        vap_power.charge = 10
    sim3.world.add_entity(vaporator)
    scenarios.append(("GX1 Vaporator Low Power Test", sim3))
    
    return scenarios
