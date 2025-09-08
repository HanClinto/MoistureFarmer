import pytest
from simulation.core.World import World
from simulation.core.entity.Entity import Location
from simulation.core.entity.Chassis import Chassis
from simulation.core.entity.ComponentSlot import ComponentSlot
from simulation.core.entity.component.Component import Component
from simulation.core.entity.component.CondenserUnit import CondenserUnit
from simulation.core.entity.component.Gripper import Gripper
from simulation.core.entity.component.PowerPack import PowerPack, SmallPowerPack
from simulation.core.entity.component.Storage import Storage, SmallStorage
from simulation.llm.ToolCall import ToolCallState

# Force model rebuild for components to fix forward reference issues
World.model_rebuild()
Chassis.model_rebuild()
ComponentSlot.model_rebuild()
Component.model_rebuild()
Storage.model_rebuild()
Gripper.model_rebuild()
CondenserUnit.model_rebuild()
PowerPack.model_rebuild()
SmallPowerPack.model_rebuild()
SmallStorage.model_rebuild()


# Simple test chassis classes
class TestDroid(Chassis):
    """Simple droid for testing with gripper and storage slots."""
    slots: dict[str, ComponentSlot] = {
        "gripper": ComponentSlot(accepts=Gripper),
        "storage": ComponentSlot(accepts=SmallStorage),
        "power": ComponentSlot(accepts=PowerPack),
    }


class TestVaporator(Chassis):
    """Simple vaporator for testing with condenser and power slots."""
    slots: dict[str, ComponentSlot] = {
        "condenser": ComponentSlot(accepts=CondenserUnit),
        "power_pack": ComponentSlot(accepts=PowerPack),
    }


class TestVaporatorWithStorage(Chassis):
    """Vaporator with storage slot for testing storage operations.""" 
    slots: dict[str, ComponentSlot] = {
        "condenser": ComponentSlot(accepts=CondenserUnit),
        "power_pack": ComponentSlot(accepts=PowerPack),
        "storage": ComponentSlot(accepts=SmallStorage),
    }


class TestGripperIntegration:
    """Integration tests for Gripper component functionality."""
    
    def setup_method(self):
        """Set up test environment with test droid and vaporators."""
        self.world = World()
        
        # Create test droid with Gripper and Storage
        self.droid = TestDroid(id="test_droid", location=Location(x=5, y=5))
        self.gripper = Gripper(id="gripper_1")
        self.storage = SmallStorage(id="storage_1")
        self.droid_power = SmallPowerPack(id="droid_power")
        
        # Install components in droid
        self.droid.install_component("gripper", self.gripper)
        self.droid.install_component("storage", self.storage)
        self.droid.install_component("power", self.droid_power)
        
        # Create two test vaporators
        self.vaporator1 = TestVaporator(id="vap1", location=Location(x=4, y=5))  # Adjacent (left)
        self.vaporator2 = TestVaporator(id="vap2", location=Location(x=6, y=5))  # Adjacent (right)
        
        # Install default components in vaporators
        self.vap1_condenser = CondenserUnit(id="vap1_condenser")
        self.vap1_power = SmallPowerPack(id="vap1_power")
        self.vap2_condenser = CondenserUnit(id="vap2_condenser")
        self.vap2_power = SmallPowerPack(id="vap2_power")
        
        self.vaporator1.install_component("condenser", self.vap1_condenser)
        self.vaporator1.install_component("power_pack", self.vap1_power)
        self.vaporator2.install_component("condenser", self.vap2_condenser)
        self.vaporator2.install_component("power_pack", self.vap2_power)
        
        # Add all entities to world
        self.world.add_entity(self.droid)
        self.world.add_entity(self.vaporator1)
        self.world.add_entity(self.vaporator2)
    
    def test_pull_component_from_chassis_slot(self):
        """Test pulling a component from a chassis slot."""
        # Pull the condenser from vaporator1
        result = self.gripper.pull_component("vap1_condenser", "vap1")
        
        assert result.state == ToolCallState.SUCCESS
        assert len(self.gripper.inventory) == 1
        assert self.gripper.inventory[0] is self.vap1_condenser
        assert self.vaporator1.slots["condenser"].component is None
        assert self.vap1_condenser.chassis is None
        assert self.vap1_condenser.storage_parent is self.gripper
    
    def test_pull_component_by_type(self):
        """Test pulling a component by type name."""
        # Pull a CondenserUnit from vaporator1 (should find vap1_condenser)
        result = self.gripper.pull_component("CondenserUnit", "vap1")
        
        assert result.state == ToolCallState.SUCCESS
        assert len(self.gripper.inventory) == 1
        assert isinstance(self.gripper.inventory[0], CondenserUnit)
        assert self.vaporator1.slots["condenser"].component is None
    
    def test_pull_component_adjacency_check(self):
        """Test that pull_component requires adjacency."""
        # Create a distant vaporator
        distant_vap = TestVaporator(id="distant_vap", location=Location(x=10, y=10))
        distant_condenser = CondenserUnit(id="distant_condenser")
        distant_vap.install_component("condenser", distant_condenser)
        self.world.add_entity(distant_vap)
        
        # Try to pull from it (should fail)
        result = self.gripper.pull_component("distant_condenser", "distant_vap")
        
        assert result.state == ToolCallState.FAILURE
        assert "not adjacent" in result.message
        assert len(self.gripper.inventory) == 0
    
    def test_pull_component_when_gripper_full(self):
        """Test that pull_component fails when gripper already holds a component."""
        # First pull a component
        result1 = self.gripper.pull_component("vap1_condenser", "vap1")
        assert result1.state == ToolCallState.SUCCESS
        
        # Try to pull another (should fail)
        result2 = self.gripper.pull_component("vap2_condenser", "vap2")
        assert result2.state == ToolCallState.FAILURE
        assert "already holding" in result2.message
    
    def test_install_component_success(self):
        """Test successful component installation."""
        # First pull a component
        result1 = self.gripper.pull_component("vap1_condenser", "vap1")
        assert result1.state == ToolCallState.SUCCESS
        
        # Remove condenser from vaporator2 to make room
        self.vaporator2.slots["condenser"].component = None
        self.vap2_condenser.chassis = None
        
        # Install the pulled component in vaporator2
        result2 = self.gripper.install_component("vap2")
        
        assert result2.state == ToolCallState.SUCCESS
        assert len(self.gripper.inventory) == 0
        assert self.vaporator2.slots["condenser"].component is self.vap1_condenser
        assert self.vap1_condenser.chassis is self.vaporator2
    
    def test_install_component_no_compatible_slot(self):
        """Test installation failure when no compatible slot exists."""
        # Pull a PowerPack
        result1 = self.gripper.pull_component("vap1_power", "vap1")
        assert result1.state == ToolCallState.SUCCESS
        
        # Try to install in vaporator2, but its power_pack slot is already occupied
        result2 = self.gripper.install_component("vap2")
        
        # This should fail because vaporator2 already has a power pack
        assert result2.state == ToolCallState.FAILURE
        assert "No compatible empty slot found" in result2.message
    
    def test_install_component_adjacency_check(self):
        """Test that install_component requires adjacency."""
        # First pull a component
        result1 = self.gripper.pull_component("vap1_condenser", "vap1")
        assert result1.state == ToolCallState.SUCCESS
        
        # Create distant entity
        distant_vap = TestVaporator(id="distant_vap", location=Location(x=10, y=10))
        self.world.add_entity(distant_vap)
        
        # Try to install (should fail)
        result2 = self.gripper.install_component("distant_vap")
        
        assert result2.state == ToolCallState.FAILURE
        assert "not adjacent" in result2.message
    
    def test_store_component_in_own_entity(self):
        """Test storing component in our own entity's storage."""
        # First pull a component
        result1 = self.gripper.pull_component("vap1_condenser", "vap1")
        assert result1.state == ToolCallState.SUCCESS
        
        # Store it in our own storage (no target_entity specified)
        result2 = self.gripper.store_component()
        
        assert result2.state == ToolCallState.SUCCESS
        assert len(self.gripper.inventory) == 0
        assert len(self.storage.inventory) == 1
        assert self.storage.inventory[0] is self.vap1_condenser
    
    def test_store_component_in_target_entity(self):
        """Test storing component in another entity's storage."""
        # Create a vaporator with storage slot and install storage
        vaporator_with_storage = TestVaporatorWithStorage(id="vap_with_storage", location=Location(x=4, y=5))
        vap_storage = SmallStorage(id="vap_storage")
        vaporator_with_storage.install_component("storage", vap_storage)
        self.world.add_entity(vaporator_with_storage)
        
        # First pull a component
        result1 = self.gripper.pull_component("vap2_condenser", "vap2")
        assert result1.state == ToolCallState.SUCCESS
        
        # Store it in the vaporator's storage
        result2 = self.gripper.store_component("vap_with_storage")
        
        assert result2.state == ToolCallState.SUCCESS
        assert len(self.gripper.inventory) == 0
        assert len(vap_storage.inventory) == 1
        assert vap_storage.inventory[0] is self.vap2_condenser
    
    def test_unstore_component_success(self):
        """Test retrieving component from storage."""
        # First store a component in our storage
        test_condenser = CondenserUnit(id="test_condenser")
        self.storage.add_component(test_condenser)
        
        # Retrieve it
        result = self.gripper.unstore_component("test_condenser")
        
        assert result.state == ToolCallState.SUCCESS
        assert len(self.gripper.inventory) == 1
        assert self.gripper.inventory[0] is test_condenser
        assert test_condenser not in self.storage.inventory
    
    def test_unstore_component_by_type(self):
        """Test retrieving component by type from storage."""
        # First store a component in our storage
        test_condenser = CondenserUnit(id="test_condenser")
        self.storage.add_component(test_condenser)
        
        # Retrieve by type
        result = self.gripper.unstore_component("CondenserUnit")
        
        assert result.state == ToolCallState.SUCCESS
        assert len(self.gripper.inventory) == 1
        assert isinstance(self.gripper.inventory[0], CondenserUnit)
    
    def test_unstore_component_when_gripper_full(self):
        """Test that unstore_component fails when gripper is full."""
        # First fill the gripper
        result1 = self.gripper.pull_component("vap1_condenser", "vap1")
        assert result1.state == ToolCallState.SUCCESS
        
        # Add a component to storage
        test_power = SmallPowerPack(id="test_power")
        self.storage.add_component(test_power)
        
        # Try to retrieve from storage
        result2 = self.gripper.unstore_component("test_power")
        
        assert result2.state == ToolCallState.FAILURE
        assert "already holding" in result2.message
    
    def test_unstore_component_not_found(self):
        """Test unstore_component when component doesn't exist."""
        result = self.gripper.unstore_component("NonExistentComponent")
        
        assert result.state == ToolCallState.FAILURE
        assert "not found" in result.message
    
    def test_complete_manipulation_workflow(self):
        """Test complete workflow: pull -> install -> pull -> install."""
        # Step 1: Pull condenser from vaporator1
        result1 = self.gripper.pull_component("vap1_condenser", "vap1")
        assert result1.state == ToolCallState.SUCCESS
        
        # Step 2: Remove condenser from vaporator2 to make room
        self.vaporator2.slots["condenser"].component = None
        self.vap2_condenser.chassis = None
        
        # Step 3: Install condenser in vaporator2
        result2 = self.gripper.install_component("vap2")
        assert result2.state == ToolCallState.SUCCESS
        
        # Step 4: Pull power pack from vaporator1
        result3 = self.gripper.pull_component("vap1_power", "vap1")
        assert result3.state == ToolCallState.SUCCESS
        
        # Step 5: Remove power pack from vaporator2 to make room
        self.vaporator2.slots["power_pack"].component = None
        self.vap2_power.chassis = None
        
        # Step 6: Install power pack in vaporator2
        result4 = self.gripper.install_component("vap2")
        assert result4.state == ToolCallState.SUCCESS
        
        # Verify final state
        assert self.vaporator1.slots["condenser"].component is None
        assert self.vaporator1.slots["power_pack"].component is None
        assert self.vaporator2.slots["condenser"].component is self.vap1_condenser
        assert self.vaporator2.slots["power_pack"].component is self.vap1_power
        assert len(self.gripper.inventory) == 0
    
    def test_simulation_tick_with_manipulated_components(self):
        """Test that manipulated components work correctly during simulation ticks."""
        # Complete the manipulation workflow first
        self.test_complete_manipulation_workflow()
        
        # Now tick the world and verify components work
        # This is a basic test - components should tick without errors
        self.world.tick()
        
        # Both vaporators should have their components properly installed
        assert self.vaporator2.slots["condenser"].component is not None
        assert self.vaporator2.slots["power_pack"].component is not None
        
        # Components should have proper chassis references
        assert self.vaporator2.slots["condenser"].component.chassis is self.vaporator2
        assert self.vaporator2.slots["power_pack"].component.chassis is self.vaporator2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])