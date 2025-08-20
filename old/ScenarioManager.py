import json
from typing import Dict, List, Any, Type, Optional
from pydantic import BaseModel, Field
from pathlib import Path

from simulation.Entity import Entity, Location
from simulation.World import Simulation, World
from simulation.DroidModels import GonkDroid, R2Astromech
from simulation.Vaporator import GX1_Vaporator, GX8_Vaporator
from simulation.Component import PowerPack, SmallPowerPack, Component


class EntityTemplate(BaseModel):
    """Template for creating entities from JSON"""
    type: str  # Class name like "GonkDroid", "GX1_Vaporator"
    id: Optional[str] = None
    location: Optional[Location] = None
    # Additional fields for entity-specific properties
    properties: Dict[str, Any] = Field(default_factory=dict)
    # Component modifications (e.g., set power levels, etc.)
    component_overrides: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class ScenarioTemplate(BaseModel):
    """Template for defining complete scenarios"""
    name: str
    description: Optional[str] = None
    simulation_settings: Dict[str, Any] = Field(default_factory=dict)
    entities: List[EntityTemplate] = Field(default_factory=list)


class ScenarioManager:
    """Manager for loading/saving scenarios to/from JSON"""
    
    # Registry of available entity types
    ENTITY_TYPES: Dict[str, Type[Entity]] = {
        "GonkDroid": GonkDroid,
        "R2Astromech": R2Astromech,
        "GX1_Vaporator": GX1_Vaporator,
        "GX8_Vaporator": GX8_Vaporator,
    }
    
    @classmethod
    def save_scenario_to_json(cls, scenario: ScenarioTemplate, file_path: str) -> None:
        """Save a scenario template to JSON file"""
        # Use exclude_defaults=True to only save non-default values
        scenario_dict = scenario.model_dump(exclude_defaults=True, exclude_none=True)
        
        with open(file_path, 'w') as f:
            json.dump(scenario_dict, f, indent=2)
    
    @classmethod
    def load_scenario_from_json(cls, file_path: str) -> ScenarioTemplate:
        """Load a scenario template from JSON file"""
        with open(file_path, 'r') as f:
            scenario_dict = json.load(f)
        
        return ScenarioTemplate.model_validate(scenario_dict)
    
    @classmethod
    def create_scenario_from_simulation(cls, simulation: Simulation, name: str, description: str = None) -> ScenarioTemplate:
        """Extract a scenario template from an existing simulation"""
        entities = []
        
        for entity in simulation.world.entities.values():
            # Get the entity type name
            entity_type = entity.__class__.__name__
            
            # Extract only the fields we need, avoiding circular references
            entity_template_data = {
                "type": entity_type,
                "location": entity.location
            }
            
            # Add other non-default entity properties, excluding 'world' and 'slots'
            entity_data = entity.model_dump(
                exclude_defaults=True, 
                exclude_none=True,
                exclude={'world', 'slots'}  # Exclude circular references and component data
            )
            
            # Remove type and location since we handle those explicitly
            entity_data.pop('type', None)
            entity_data.pop('location', None)
            
            # Only add properties if there are non-default values
            if entity_data:
                entity_template_data["properties"] = entity_data
            
            # Extract component overrides
            component_overrides = {}
            if hasattr(entity, 'slots'):
                for slot_name, slot in entity.slots.items():
                    if slot.component:
                        try:
                            # Exclude potential circular references in components
                            comp_data = slot.component.model_dump(
                                exclude_defaults=True, 
                                exclude_none=True,
                                exclude={'chassis', 'world', 'entity'}  # Exclude back-references
                            )
                            if comp_data:  # Only include if there are non-default values
                                component_overrides[slot_name] = comp_data
                        except ValueError as e:
                            if "Circular reference" in str(e):
                                print(f"Warning: Skipping component {slot_name} due to circular reference")
                                continue
                            else:
                                raise
            
            if component_overrides:
                entity_template_data["component_overrides"] = component_overrides
            
            # Create entity template using the prepared data
            entity_template = EntityTemplate(**entity_template_data)
            entities.append(entity_template)
        
        # Get simulation settings (excluding defaults)
        sim_settings = simulation.model_dump(
            exclude_defaults=True, 
            exclude_none=True,
            exclude={'world', '_on_tick_subscribers', '__instance'}
        )
        
        return ScenarioTemplate(
            name=name,
            description=description,
            simulation_settings=sim_settings,
            entities=entities
        )
    
    @classmethod
    def load_scenario_into_simulation(cls, scenario: ScenarioTemplate, simulation: Simulation = None) -> Simulation:
        """Load a scenario template into a simulation"""
        if simulation is None:
            simulation = Simulation()
        
        # Apply simulation settings
        for key, value in scenario.simulation_settings.items():
            if hasattr(simulation, key):
                setattr(simulation, key, value)
        
        # Create and add entities
        for entity_template in scenario.entities:
            entity = cls._create_entity_from_template(entity_template)
            simulation.world.add_entity(entity)
        
        return simulation
    
    @classmethod
    def _create_entity_from_template(cls, template: EntityTemplate) -> Entity:
        """Create an entity instance from a template"""
        if template.type not in cls.ENTITY_TYPES:
            raise ValueError(f"Unknown entity type: {template.type}")
        
        EntityClass = cls.ENTITY_TYPES[template.type]
        
        # Start with template properties
        entity_data = template.properties.copy()
        
        # Add location if specified
        if template.location:
            entity_data['location'] = template.location
        
        # Add ID if specified
        if template.id:
            entity_data['id'] = template.id
        
        # Create the entity
        entity = EntityClass(**entity_data)
        
        # Apply component overrides
        if hasattr(entity, 'slots') and template.component_overrides:
            for slot_name, component_data in template.component_overrides.items():
                if slot_name in entity.slots and entity.slots[slot_name].component:
                    component = entity.slots[slot_name].component
                    
                    # Apply the overrides to the component
                    for key, value in component_data.items():
                        if hasattr(component, key):
                            setattr(component, key, value)
        
        return entity


# Convenience functions for common operations
def save_simulation_as_scenario(simulation: Simulation, name: str, file_path: str, description: str = None):
    """Save current simulation state as a scenario"""
    scenario = ScenarioManager.create_scenario_from_simulation(simulation, name, description)
    ScenarioManager.save_scenario_to_json(scenario, file_path)


def load_scenario(file_path: str) -> Simulation:
    """Load a scenario and return a configured simulation"""
    scenario = ScenarioManager.load_scenario_from_json(file_path)
    return ScenarioManager.load_scenario_into_simulation(scenario)


def create_test_scenarios():
    """Create example scenarios based on your test cases"""
    
    # Scenario 1: Droid Movement Test
    droid_movement_scenario = ScenarioTemplate(
        name="Droid Movement Test",
        description="Test basic droid movement capabilities",
        simulation_settings={
            "simulation_delay": 0
        },
        entities=[
            EntityTemplate(
                type="GonkDroid",
                location=Location(x=0, y=0),
                component_overrides={
                    "motivator": {
                        "destination": {"x": 25, "y": -25}
                    }
                }
            )
        ]
    )
    
    # Scenario 2: Low Battery Droid Test
    low_battery_scenario = ScenarioTemplate(
        name="Low Battery Droid Test",
        description="Test droid behavior with limited power",
        simulation_settings={
            "simulation_delay": 0
        },
        entities=[
            EntityTemplate(
                type="GonkDroid",
                location=Location(x=0, y=0),
                component_overrides={
                    "power_pack": {
                        "charge": 10
                    },
                    "motivator": {
                        "destination": {"x": 25, "y": -25}
                    }
                }
            )
        ]
    )
    
    # Scenario 3: Vaporator with Low Power
    vaporator_low_power_scenario = ScenarioTemplate(
        name="GX1 Vaporator Low Power Test",
        description="Test vaporator with limited starting power",
        simulation_settings={
            "simulation_delay": 0
        },
        entities=[
            EntityTemplate(
                type="GX1_Vaporator",
                location=Location(x=0, y=0),
                component_overrides={
                    "power_pack": {
                        "charge": 10
                    }
                }
            )
        ]
    )
    
    return [droid_movement_scenario, low_battery_scenario, vaporator_low_power_scenario]
