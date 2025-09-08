from typing import List, Optional, Union
from simulation.core.entity.component.Storage import Storage
from simulation.core.entity.component.Component import Component
from simulation.llm.ToolCall import ToolCallResult, ToolCallState, tool


class Gripper(Storage):
    """Gripper component for manipulating components in other entities.
    
    The Gripper is a specialized Storage component with capacity for 1 component
    that can manipulate components in adjacent entities. It provides tool calls
    for pulling components from other entities, installing held components,
    and managing component storage.
    """
    name: str = "Component Gripper"
    description: str = "Manipulator for installing and removing components from adjacent entities"
    capacity: int = 1

    @tool
    def pull_component(self, target_component: str, target_entity: str) -> ToolCallResult:
        """Pull a component from an adjacent entity.
        
        Takes a component from an adjacent entity - either from its ComponentSlots
        or from any of its Storage components' inventories - and places it into
        the gripper's inventory.
        
        Args:
            target_component (str): Component identifier (type name or ID)
            target_entity (str): Entity identifier (type name or ID)
            
        Returns:
            ToolCallResult with success/failure status
        """
        # Check if gripper already has a component
        if not self.inventory == []:
            return ToolCallResult(
                state=ToolCallState.FAILURE,
                message=f"Gripper already holding component {self.inventory[0].id}. Cannot pull another component."
            )
        
        # Find target entity
        if not self.chassis or not self.chassis.world:
            return ToolCallResult(
                state=ToolCallState.FAILURE,
                message="Gripper is not installed in a chassis or chassis is not in a world."
            )
        
        entities = self.chassis.world.get_entities(target_entity)
        if not entities:
            return ToolCallResult(
                state=ToolCallState.FAILURE,
                message=f"No entities found with identifier '{target_entity}'."
            )
        
        # Sort by distance and check adjacency
        entities.sort(key=lambda e: self.chassis.location.distance_to(e.location))
        entity = entities[0]
        
        distance = self.chassis.location.distance_to(entity.location)
        if distance > 1:
            return ToolCallResult(
                state=ToolCallState.FAILURE,
                message=f"Entity {entity.id} is not adjacent (distance: {distance}). Must be adjacent (distance ≤ 1)."
            )
        
        # Find target component
        found_component = None
        
        # Check if entity has slots (Chassis)
        if hasattr(entity, 'slots'):
            # Search in chassis slots
            for slot_id, slot in entity.slots.items():
                if slot.component:
                    if (slot.component.id == target_component or 
                        slot.component.__class__.__name__ == target_component):
                        found_component = slot.component
                        # Remove from slot
                        slot.component = None
                        found_component.chassis = None
                        found_component.storage_parent = None
                        break
        
        # If not found in slots, search in Storage components
        if not found_component and hasattr(entity, 'components'):
            for comp in entity.components:
                if isinstance(comp, Storage):
                    for stored_comp in comp.inventory:
                        if (stored_comp.id == target_component or 
                            stored_comp.__class__.__name__ == target_component):
                            found_component = stored_comp
                            comp.remove_component(stored_comp)
                            break
                    if found_component:
                        break
        
        if not found_component:
            return ToolCallResult(
                state=ToolCallState.FAILURE,
                message=f"Component '{target_component}' not found in entity '{entity.id}'."
            )
        
        # Add to gripper inventory
        self.inventory.append(found_component)
        found_component.storage_parent = self
        found_component.chassis = None
        
        return ToolCallResult(
            state=ToolCallState.SUCCESS,
            message=f"Successfully pulled component {found_component.id} from entity {entity.id}."
        )

    @tool
    def install_component(self, target_entity: str) -> ToolCallResult:
        """Install the currently held component into a target entity.
        
        Installs the component held in the gripper's inventory into the first
        matching ComponentSlot in the target entity.
        
        Args:
            target_entity (str): Entity identifier (type name or ID)
            
        Returns:
            ToolCallResult with success/failure status
        """
        # Check if gripper has a component
        if not self.inventory:
            return ToolCallResult(
                state=ToolCallState.FAILURE,
                message="Gripper is not holding any component to install."
            )
        
        component_to_install = self.inventory[0]
        
        # Find target entity
        if not self.chassis or not self.chassis.world:
            return ToolCallResult(
                state=ToolCallState.FAILURE,
                message="Gripper is not installed in a chassis or chassis is not in a world."
            )
        
        entities = self.chassis.world.get_entities(target_entity)
        if not entities:
            return ToolCallResult(
                state=ToolCallState.FAILURE,
                message=f"No entities found with identifier '{target_entity}'."
            )
        
        # Sort by distance and check adjacency
        entities.sort(key=lambda e: self.chassis.location.distance_to(e.location))
        entity = entities[0]
        
        distance = self.chassis.location.distance_to(entity.location)
        if distance > 1:
            return ToolCallResult(
                state=ToolCallState.FAILURE,
                message=f"Entity {entity.id} is not adjacent (distance: {distance}). Must be adjacent (distance ≤ 1)."
            )
        
        # Find compatible slot
        if not hasattr(entity, 'slots'):
            return ToolCallResult(
                state=ToolCallState.FAILURE,
                message=f"Entity {entity.id} does not have component slots."
            )
        
        compatible_slot = None
        for slot_id, slot in entity.slots.items():
            if slot.component is None and isinstance(component_to_install, slot.accepts):
                compatible_slot = slot
                break
        
        if not compatible_slot:
            return ToolCallResult(
                state=ToolCallState.FAILURE,
                message=f"No compatible empty slot found for component {component_to_install.__class__.__name__} in entity {entity.id}."
            )
        
        # Install component
        self.inventory.remove(component_to_install)
        component_to_install.storage_parent = None
        compatible_slot.component = component_to_install
        component_to_install.chassis = entity
        
        # Call on_installed if the method exists
        if hasattr(component_to_install, 'on_installed'):
            component_to_install.on_installed(entity)
        
        return ToolCallResult(
            state=ToolCallState.SUCCESS,
            message=f"Successfully installed component {component_to_install.id} into entity {entity.id}."
        )

    @tool
    def store_component(self, target_entity: Optional[str] = None) -> ToolCallResult:
        """Store the currently held component into a Storage component.
        
        Stores the component held in the gripper's inventory into the first
        available Storage component with capacity. If no target entity is
        specified, stores into our own entity's Storage components.
        
        Args:
            target_entity (Optional[str]): Optional entity identifier (type name or ID)
            
        Returns:
            ToolCallResult with success/failure status
        """
        # Check if gripper has a component
        if not self.inventory:
            return ToolCallResult(
                state=ToolCallState.FAILURE,
                message="Gripper is not holding any component to store."
            )
        
        component_to_store = self.inventory[0]
        
        if not self.chassis or not self.chassis.world:
            return ToolCallResult(
                state=ToolCallState.FAILURE,
                message="Gripper is not installed in a chassis or chassis is not in a world."
            )
        
        # Determine target entity
        target_entity_obj = self.chassis  # Default to our own entity
        
        if target_entity:
            entities = self.chassis.world.get_entities(target_entity)
            if not entities:
                return ToolCallResult(
                    state=ToolCallState.FAILURE,
                    message=f"No entities found with identifier '{target_entity}'."
                )
            
            # Sort by distance and check adjacency
            entities.sort(key=lambda e: self.chassis.location.distance_to(e.location))
            target_entity_obj = entities[0]
            
            distance = self.chassis.location.distance_to(target_entity_obj.location)
            if distance > 1:
                return ToolCallResult(
                    state=ToolCallState.FAILURE,
                    message=f"Entity {target_entity_obj.id} is not adjacent (distance: {distance}). Must be adjacent (distance ≤ 1)."
                )
        
        # Find Storage component with available capacity
        storage_component = None
        if hasattr(target_entity_obj, 'components'):
            for comp in target_entity_obj.components:
                if isinstance(comp, Storage) and comp is not self and comp.available_capacity > 0:
                    storage_component = comp
                    break
        
        if not storage_component:
            entity_name = target_entity_obj.id if target_entity else "own entity"
            return ToolCallResult(
                state=ToolCallState.FAILURE,
                message=f"No Storage component with available capacity found in {entity_name}."
            )
        
        # Store component
        if storage_component.add_component(component_to_store):
            # The add_component method already handles removing from previous location
            # so we just need to ensure our inventory is updated if it wasn't already
            if component_to_store in self.inventory:
                self.inventory.remove(component_to_store)
            return ToolCallResult(
                state=ToolCallState.SUCCESS,
                message=f"Successfully stored component {component_to_store.id} in {storage_component.id}."
            )
        else:
            return ToolCallResult(
                state=ToolCallState.FAILURE,
                message=f"Failed to store component {component_to_store.id} in storage {storage_component.id}."
            )

    @tool
    def unstore_component(self, target_component: str) -> ToolCallResult:
        """Retrieve a component from other Storage components in this entity.
        
        Searches other Storage components in this entity for the specified
        component and makes it the currently held component.
        
        Args:
            target_component (str): Component identifier (type name or ID)
            
        Returns:
            ToolCallResult with success/failure status
        """
        # Check if gripper already has a component
        if self.inventory:
            return ToolCallResult(
                state=ToolCallState.FAILURE,
                message=f"Gripper already holding component {self.inventory[0].id}. Cannot retrieve another component."
            )
        
        if not self.chassis:
            return ToolCallResult(
                state=ToolCallState.FAILURE,
                message="Gripper is not installed in a chassis."
            )
        
        # Search in other Storage components
        found_component = None
        source_storage = None
        
        if hasattr(self.chassis, 'components'):
            for comp in self.chassis.components:
                if isinstance(comp, Storage) and comp is not self:
                    for stored_comp in comp.inventory:
                        if (stored_comp.id == target_component or 
                            stored_comp.__class__.__name__ == target_component):
                            found_component = stored_comp
                            source_storage = comp
                            break
                    if found_component:
                        break
        
        if not found_component:
            return ToolCallResult(
                state=ToolCallState.FAILURE,
                message=f"Component '{target_component}' not found in any Storage component of this entity."
            )
        
        # Move component from source storage to gripper
        if source_storage.remove_component(found_component):
            self.inventory.append(found_component)
            found_component.storage_parent = self
            return ToolCallResult(
                state=ToolCallState.SUCCESS,
                message=f"Successfully retrieved component {found_component.id} from storage {source_storage.id}."
            )
        else:
            return ToolCallResult(
                state=ToolCallState.FAILURE,
                message=f"Failed to remove component {found_component.id} from storage {source_storage.id}."
            )