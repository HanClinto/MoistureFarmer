import pytest
from simulation.core.World import World
from simulation.core.entity.Entity import Location
from simulation.core.entity.Chassis import Chassis
from simulation.core.entity.ComponentSlot import ComponentSlot
from simulation.core.entity.component.Component import Component
from simulation.core.entity.component.CondenserUnit import CondenserUnit
from simulation.core.entity.component.Gripper import Gripper
from simulation.core.entity.component.PowerPack import PowerPack, SmallPowerPack
from simulation.core.entity.component.Storage import LargeStorage, Storage, SmallStorage
from simulation.core.entity.component.Motivator import Motivator
from simulation.equipment.DroidModels import R2Astromech
from simulation.equipment.VaporatorModels import GX1_Vaporator
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
LargeStorage.model_rebuild()
Motivator.model_rebuild()
R2Astromech.model_rebuild()
GX1_Vaporator.model_rebuild()


class SimpleChassis(Chassis):
    """Simple chassis for testing with storage slot."""
    slots: dict[str, ComponentSlot] = {
        "storage": ComponentSlot(accepts=Storage, default_component=LargeStorage),
        "power": ComponentSlot(accepts=PowerPack, default_component=SmallPowerPack),
    }

class TestGripper:
    """Test suite for Gripper component functionality."""

    def setup_method(self):
        """Set up test environment with R2 droid and two Vaporators."""
        self.world = World()

        # Create R2 droid with Gripper and Storage
        self.r2 = R2Astromech(id="r2_test", location=Location(x=5, y=5))
        self.r2_gripper = Gripper(id="gripper_1")
        self.r2_storage = SmallStorage(id="storage_1")

        # Install gripper and storage in R2
        self.r2.install_component("gripper", self.r2_gripper)
        self.r2.install_component("storage", self.r2_storage)

        # Create two Vaporators
        self.vaporator1 = GX1_Vaporator(id="vap1", location=Location(x=4, y=5))  # Adjacent (left)
        self.vaporator2 = GX1_Vaporator(id="vap2", location=Location(x=6, y=5))  # Adjacent (right)

        # Remove specific components from vaporators to test manipulation
        # Remove Condenser from vaporator1
        condenser1 = self.vaporator1.uninstall_component("condenser")

        # Remove PowerPack from vaporator2
        powerpack2 = self.vaporator2.uninstall_component("power_pack")

        # Store these components in our R2's storage for testing
        if condenser1:
            self.r2_storage.store_component(condenser1)
        if powerpack2:
            self.r2_storage.store_component(powerpack2)

        # Create a storage container
        self.storage_container = SimpleChassis(id="storage_container", location=Location(x=5, y=4)) # Adjacent (top)

        # Add all entities to world
        self.world.add_entity(self.r2)
        self.world.add_entity(self.vaporator1)
        self.world.add_entity(self.vaporator2)
        self.world.add_entity(self.storage_container)

    def test_gripper_basic_properties(self):
        """Test basic Gripper properties."""
        assert self.r2_gripper.name == "Component Gripper"
        assert self.r2_gripper.held_component is None

    def test_pull_component_from_chassis_slot(self):
        """Test pulling a component from a chassis slot."""
        # vaporator2 should have a WaterTank we can pull
        water_tank = self.vaporator2.slots["water_tank"].component
        assert water_tank is not None

        # Pull the water tank
        result = self.r2_gripper.pull_component("WaterTank", "vap2")

        assert result.state == ToolCallState.SUCCESS
        assert self.r2_gripper.held_component is water_tank
        assert self.vaporator2.slots["water_tank"].component is None
        assert water_tank.chassis is None
        assert water_tank.storage_parent is self.r2_gripper

    def test_pull_component_from_storage(self):
        """Test pulling a component from another entity's storage."""
        # First, put a component in the storage container
        test_component = CondenserUnit(id="test_condenser")
        storage1 = self.storage_container.get_component(Storage)
        storage1.store_component(test_component)

        # Pull the component from storage
        result = self.r2_gripper.pull_component("test_condenser", "storage_container")

        assert result.state == ToolCallState.SUCCESS
        assert self.r2_gripper.held_component is test_component
        assert test_component not in storage1.inventory

    def test_pull_component_from_storage_by_type(self):
        """Test pulling a component from another entity's storage."""
        # First, put a component in the storage container
        test_component = CondenserUnit(id="test_condenser")
        storage1 = self.storage_container.get_component(Storage)
        storage1.store_component(test_component)

        # Pull the component from storage
        result = self.r2_gripper.pull_component("CondenserUnit", "storage_container")

        assert result.state == ToolCallState.SUCCESS
        assert self.r2_gripper.held_component is test_component
        assert test_component not in storage1.inventory

    def test_pull_component_adjacency_check(self):
        """Test that pull_component requires adjacency."""
        # Create a distant vaporator
        distant_vap = GX1_Vaporator(id="distant_vap", location=Location(x=10, y=10))
        self.world.add_entity(distant_vap)

        # Try to pull from it (should fail)
        result = self.r2_gripper.pull_component("WaterTank", "distant_vap")

        assert result.state == ToolCallState.FAILURE
        assert "not adjacent" in result.message
        assert self.r2_gripper.held_component is None

    def test_pull_component_when_gripper_full(self):
        """Test that pull_component fails when gripper already holds a component."""
        # First pull a component
        result1 = self.r2_gripper.pull_component("WaterTank", "vap2")
        assert result1.state == ToolCallState.SUCCESS

        # Try to pull another (should fail)
        result2 = self.r2_gripper.pull_component("WaterTank", "vap1")

        assert result2.state == ToolCallState.FAILURE
        assert "already holding" in result2.message

    def test_install_component_success(self):
        """Test successful component installation."""
        # First, get a component to install by retrieving from storage
        result1 = self.r2_gripper.unstore_component("CondenserUnit")
        assert result1.state == ToolCallState.SUCCESS

        # Install it in vaporator1 (which is missing its condenser)
        result2 = self.r2_gripper.install_component("vap1")

        assert result2.state == ToolCallState.SUCCESS
        assert self.r2_gripper.held_component is None
        assert self.vaporator1.slots["condenser"].component is not None
        assert isinstance(self.vaporator1.slots["condenser"].component, CondenserUnit)

    def test_install_component_no_compatible_slot(self):
        """Test installation failure when no compatible slot exists."""
        # Get a PowerPack to install
        result1 = self.r2_gripper.unstore_component("SmallPowerPack")
        assert result1.state == ToolCallState.SUCCESS

        # Try to install in vaporator1, but its power_pack slot is already occupied
        result2 = self.r2_gripper.install_component("vap1")

        # This should fail because vaporator1 already has a power pack
        assert result2.state == ToolCallState.FAILURE
        assert "No compatible empty slot found" in result2.message

    def test_install_component_adjacency_check(self):
        """Test that install_component requires adjacency."""
        # Get a component to install
        result1 = self.r2_gripper.unstore_component("CondenserUnit")
        assert result1.state == ToolCallState.SUCCESS

        # Create distant entity
        distant_vap = GX1_Vaporator(id="distant_vap", location=Location(x=10, y=10))
        self.world.add_entity(distant_vap)

        # Try to install (should fail)
        result2 = self.r2_gripper.install_component("distant_vap")

        assert result2.state == ToolCallState.FAILURE
        assert "not adjacent" in result2.message

    def test_store_component_in_own_entity(self):
        """Test storing component in our own entity's storage."""
        # Get a component to store
        result1 = self.r2_gripper.unstore_component("CondenserUnit")
        assert result1.state == ToolCallState.SUCCESS

        # Assert our held component is of type CondenserUnit
        assert isinstance(self.r2_gripper.held_component, CondenserUnit)

        # We should now be down to 1 item in our inventory
        assert len(self.r2_storage.inventory) == 1 # Should have the SmallPowerPack still

        # Store it back (no target_entity specified)
        result2 = self.r2_gripper.store_component()
        assert result2.state == ToolCallState.SUCCESS

        assert self.r2_gripper.held_component is None
        # Should be back in our storage
        assert len(self.r2_storage.inventory) == 2  # Should be back to having both components

    def test_store_component_in_target_entity(self):
        """Test storing component in another entity's storage."""

        # Get a component to store
        result1 = self.r2_gripper.unstore_component("CondenserUnit")
        assert result1.state == ToolCallState.SUCCESS

        # We don't yet have anything in our storage container
        assert len(self.storage_container.get_component(Storage).inventory) == 0

        # Store it in storage container
        result2 = self.r2_gripper.store_component("storage_container")

        assert result2.state == ToolCallState.SUCCESS
        assert self.r2_gripper.held_component is None
        # We should now have one item in our storage container
        assert len(self.storage_container.get_component(Storage).inventory) == 1

    def test_unstore_component_success(self):
        """Test retrieving component from storage."""
        # Our storage should have components from setup
        assert len(self.r2_storage.inventory) == 2

        # Retrieve by type
        result = self.r2_gripper.unstore_component("CondenserUnit")

        assert result.state == ToolCallState.SUCCESS
        assert self.r2_gripper.held_component is not None
        assert isinstance(self.r2_gripper.held_component, CondenserUnit)
        assert len(self.r2_storage.inventory) == 1  # One less in storage

    def test_unstore_component_when_gripper_full(self):
        """Test that unstore_component fails when gripper is full."""
        # First fill the gripper
        result1 = self.r2_gripper.unstore_component("CondenserUnit")
        assert result1.state == ToolCallState.SUCCESS

        # Add a component to storage
        test_power = SmallPowerPack(id="test_power")
        self.r2_storage.store_component(test_power)

        # Try to retrieve from storage
        result2 = self.r2_gripper.unstore_component("test_power")

        assert result2.state == ToolCallState.FAILURE
        assert "already holding" in result2.message

    def test_unstore_component_not_found(self):
        """Test unstore_component when component doesn't exist."""
        result = self.r2_gripper.unstore_component("NonExistentComponent")

        assert result.state == ToolCallState.FAILURE
        assert "not found" in result.message

    def test_complete_manipulation_workflow(self):
        """Test complete workflow: unstore -> install -> pull -> store."""
        # Step 1: Retrieve condenser from storage
        result1 = self.r2_gripper.unstore_component("CondenserUnit")
        assert result1.state == ToolCallState.SUCCESS

        # Step 2: Install condenser in vaporator1 (missing condenser)
        result2 = self.r2_gripper.install_component("vap1")
        assert result2.state == ToolCallState.SUCCESS
        assert self.vaporator1.slots["condenser"].component is not None

        # Step 3: Pull power pack from vaporator1
        result3 = self.r2_gripper.pull_component("SmallPowerPack", "vap1")
        assert result3.state == ToolCallState.SUCCESS

        # Step 4: Install power pack in vaporator2 (missing power pack)
        result4 = self.r2_gripper.install_component("vap2")
        assert result4.state == ToolCallState.SUCCESS
        assert self.vaporator2.slots["power_pack"].component is not None

        # Verify both vaporators now have their components
        assert self.vaporator1.slots["condenser"].component is not None
        assert self.vaporator2.slots["power_pack"].component is not None

    def test_simulation_tick_with_manipulated_components(self):
        """Test that manipulated components work correctly during simulation ticks."""
        # Complete the manipulation workflow first
        self.test_complete_manipulation_workflow()

        # Now tick the world and verify components work
        # Note: This test verifies the components tick correctly after manipulation
        self.world.tick()

        # Both vaporators should have their required components and tick without errors
        # This is a basic test - in a real scenario, we'd verify water condensation etc.
        assert self.vaporator1.slots["condenser"].component is not None
        assert self.vaporator2.slots["power_pack"].component is not None
        # This is a basic test - in a real scenario, we'd verify water condensation etc.
        assert self.vaporator1.slots["condenser"].component is not None
        assert self.vaporator2.slots["power_pack"].component is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 