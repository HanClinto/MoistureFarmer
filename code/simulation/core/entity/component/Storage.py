from typing import List, Optional, TYPE_CHECKING
from pydantic import Field
from simulation.core.entity.component.Component import Component

if TYPE_CHECKING:
    from simulation.core.entity.ComponentSlot import ComponentSlot

class Storage(Component):
    """Storage component for carrying additional components that are not installed.
    
    Storage components allow a Chassis to carry additional components that don't 
    receive tick events but are simply carried by the Chassis. Components stored 
    in Storage are removed from their previous location when added.
    """
    name: str = "Basic Storage"
    description: str = "Storage component for carrying uninstalled components"
    capacity: int = 1
    inventory: List[Component] = Field(default_factory=list)

    def __init__(self, **data):
        super().__init__(**data)
        # No need to manually initialize inventory since Field(default_factory=list) handles it

    @property
    def available_capacity(self) -> int:
        """Get the available storage capacity."""
        return self.capacity - len(self.inventory)

    @property
    def is_full(self) -> bool:
        """Check if storage is at full capacity."""
        return len(self.inventory) >= self.capacity

    def add_component(self, component: Component) -> bool:
        """Add a component to storage.
        
        Removes the component from its previous location (either a Slot or Storage object)
        and adds it to this Storage's inventory if there is available capacity.
        
        Args:
            component: The component to add to storage
            
        Returns:
            bool: True if component was successfully added, False otherwise
        """
        if self.is_full:
            self.error(f"Storage {self.id} is at full capacity ({self.capacity}). Cannot add component {component.id}.")
            return False
        
        # Remove component from its previous location
        if not self._remove_component_from_previous_location(component):
            self.error(f"Failed to remove component {component.id} from its previous location.")
            return False
        
        # Add to our inventory
        self.inventory.append(component)
        component.chassis = None  # Components in storage are not installed in chassis
        component.storage_parent = self  # Set storage parent reference
        self.info(f"Component {component.id} added to storage {self.id}. Available capacity: {self.available_capacity}")
        return True

    def remove_component(self, component: Component) -> bool:
        """Remove a component from storage.
        
        Args:
            component: The component to remove from storage
            
        Returns:
            bool: True if component was successfully removed, False otherwise
        """
        if component not in self.inventory:
            self.warn(f"Component {component.id} is not in storage {self.id}.")
            return False
        
        self.inventory.remove(component)
        component.storage_parent = None  # Clear storage parent reference
        self.info(f"Component {component.id} removed from storage {self.id}. Available capacity: {self.available_capacity}")
        return True

    def _remove_component_from_previous_location(self, component: Component) -> bool:
        """Remove a component from its previous location (chassis slot or storage).
        
        Args:
            component: The component to remove
            
        Returns:
            bool: True if successfully removed or no previous location, False on error
        """
        # If component has a chassis, it's installed in a slot
        if component.chassis:
            # Find the slot containing this component and remove it
            for slot_id, slot in component.chassis.slots.items():
                if slot.component is component:
                    slot.component = None
                    component.chassis = None
                    component.storage_parent = None  # Clear any storage parent reference
                    self.info(f"Removed component {component.id} from slot {slot_id} in chassis {component.chassis.id if component.chassis else 'unknown'}")
                    return True
            
            # If we get here, component has a chassis but wasn't found in any slot
            self.error(f"Component {component.id} has chassis reference but was not found in any slot.")
            return False
        
        # Check if component has a storage parent
        if component.storage_parent and hasattr(component.storage_parent, 'remove_component'):
            if component.storage_parent.remove_component(component):
                return True
            return False
        
        # Check all storage components in the world to find this component (fallback)
        if self.chassis and self.chassis.world:
            # Find all chassis in the world (entities is a dict, iterate over values)
            for entity in self.chassis.world.entities.values():
                if hasattr(entity, 'components'):
                    for comp in entity.components:
                        if isinstance(comp, Storage) and comp is not self:
                            if component in comp.inventory:
                                return comp.remove_component(component)
        
        # No previous location found, which is fine (component might be new)
        return True

    def get_component_by_type(self, component_type: type) -> Optional[Component]:
        """Get the first component of a specific type from inventory.
        
        Args:
            component_type: The type of component to find
            
        Returns:
            The first matching component or None if not found
        """
        for component in self.inventory:
            if isinstance(component, component_type):
                return component
        
        # Log error message when component type is not found
        self.error(f"Component of type {component_type.__name__} not found in storage {self.id}.")
        return None

    def get_components_by_type(self, component_type: type) -> List[Component]:
        """Get all components of a specific type from inventory.
        
        Args:
            component_type: The type of component to find
            
        Returns:
            List of matching components
        """
        return [comp for comp in self.inventory if isinstance(comp, component_type)]

    def to_json(self, short: bool = False):
        """Convert storage to JSON representation."""
        # Get base data but exclude inventory to avoid circular references
        excludes_list = {'chassis',
                         'world',
                         'entity',
                         'pending_tool_call',
                         'pending_tool_completion_callback',
                         'storage_parent',  # Exclude to avoid circular references
                         'inventory',  # Handle inventory separately to avoid circular refs
                         #'context',
                         #'session_history',
                         'function_ptr',
                         'tool_result',
                         } # Exclude back-references
        if short:
            excludes_list.add('path_to_destination')
            excludes_list.add('prompt_system')
            excludes_list.add('prompt_goal')
            excludes_list.add('prompt_status')
            excludes_list.add('queued_http_request')
            excludes_list.add('pending_tool_call_id')
            excludes_list.add('current_cooldown')
            excludes_list.add('cooldown_delay')
            excludes_list.add('context')
            excludes_list.add('session_history')
            # PowerConverter
            excludes_list.add('transfer_target')
            excludes_list.add('transfer_mode')

        props = self.model_dump(
                exclude_defaults=False,
                exclude_none=short, # Exclude None if producting a short version
                exclude=excludes_list
            )
        props['type'] = self.__class__.__name__
        
        # Add storage-specific fields
        props['capacity'] = self.capacity
        props['available_capacity'] = self.available_capacity
        # Use short=True for inventory items to avoid circular references
        props['inventory'] = [comp.to_json(short=True) for comp in self.inventory]
        return props


class SmallStorage(Storage):
    """Small storage component with capacity for 2 components."""
    name: str = "Small Storage"
    description: str = "Small storage compartment for carrying 2 components"
    capacity: int = 2


class MediumStorage(Storage):
    """Medium storage component with capacity for 5 components."""
    name: str = "Medium Storage"
    description: str = "Medium storage compartment for carrying 5 components"
    capacity: int = 5


class LargeStorage(Storage):
    """Large storage component with capacity for 25 components."""
    name: str = "Large Storage"
    description: str = "Large storage compartment for carrying 25 components"
    capacity: int = 25