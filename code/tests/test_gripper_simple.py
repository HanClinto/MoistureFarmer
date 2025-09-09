import pytest
from simulation.core.World import World
from simulation.core.entity.Chassis import Chassis
from simulation.core.entity.ComponentSlot import ComponentSlot
from simulation.core.entity.component.Component import Component
from simulation.core.entity.component.Storage import Storage
from simulation.core.entity.component.Gripper import Gripper

# Force model rebuild for components to fix forward reference issues  
World.model_rebuild()
Chassis.model_rebuild()
ComponentSlot.model_rebuild()
Component.model_rebuild()
Storage.model_rebuild()
Gripper.model_rebuild()


def test_gripper_basic():
    """Test basic Gripper instantiation and properties."""
    gripper = Gripper(id="test_gripper")
    
    # Gripper no longer exposes capacity; it holds a single component in held_component
    assert gripper.name == "Component Gripper"
    assert gripper.description == "Manipulator for installing and removing components from adjacent entities"
    assert gripper.held_component is None


def test_gripper_provides_tools():
    """Test that Gripper provides the expected tool calls."""
    gripper = Gripper(id="test_gripper")
    tools = gripper.provides_tools()
    
    expected_tools = {
        'pull_component',
        'install_component', 
        'store_component',
        'unstore_component'
    }
    
    for tool_name in expected_tools:
        assert tool_name in tools, f"Tool {tool_name} not found in gripper tools"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])