# TowCable component
# Adds an attach and detach functionality for towing adjacent entities
# This component allows entities to connect and pull other entities along with them.

from typing import Callable, Optional
from pygamegui import entity
from simulation.core.World import World
from simulation.core.entity.Chassis import Chassis
from simulation.core.entity.Entity import Entity, Location
from simulation.core.entity.component.Component import Component
from simulation.llm.ToolCall import ToolCallResult, ToolCallState, tool
from simulation.movement_intent import MovementIntent


class TowCable(Component):
    attached_entity: Optional[Chassis] = None

    def __init__(self):
        super().__init__()

    @tool
    def attach_tow_cable(self, identifier: str) -> Callable[..., ToolCallResult]:
        """
        Attach tow cable to an adjacent entity.
        An attached entity will follow along behind this entity as it moves along.
        A tow cable can only be attached to a single entity at a time.
        Args:
            identifier (str): The ID of the entity to recharge from. Must be adjacent.
        """
        world: World = self.chassis.world

        # Ensure that we don't already have something attached
        if self.attached_entity is not None:
            msg = f"Attach failed. Already attached to `{self.attached_entity.id}`."
            self.error(msg)
            return ToolCallResult(state=ToolCallState.FAILURE, message=msg)

        # Find the entity by ID and set the destination to its location
        entities = world.get_entities(identifier)

        if len(entities) == 0:
            msg = f"Attach failed. No entity found with identifier `{identifier}`."
            self.error(msg)
            return ToolCallResult(state=ToolCallState.FAILURE, message=msg)

        # Sort entities by distance to the chassis
        entities.sort(key=lambda e: self.chassis.location.distance_to(e.location))
        entity = entities[0]  # Get the closest entity

        # Check if the entity is adjacent
        distance = self.chassis.location.distance_to(entity.location)
        if not distance < 2:
            msg = f"Attach failed. `{identifier}` is {distance} units away. Must be adjacent."
            self.error(msg)
            return ToolCallResult(state=ToolCallState.FAILURE, message=msg)
        
        # Can only attach to Chassis objects
        if not isinstance(entity, Chassis):
            msg = f"Attach failed. `{identifier}` is not a Chassis."
            self.error(msg)
            return ToolCallResult(state=ToolCallState.FAILURE, message=msg)

        self.attached_entity = entity
        # HACK: Ensure that the towed entity moves after this one so that it follows correctly.
        entity.move_priority = self.chassis.move_priority + 1

        return ToolCallResult(state=ToolCallState.SUCCESS, message=f"Attach succeeded. `{identifier}` is now connected.")

    @tool
    def detach_tow_cable(self):
        """
        Detach the tow cable from the currently attached entity.
        """
        if self.attached_entity is None:
            msg = "Detach failed. No entity is currently attached."
            self.error(msg)
            return ToolCallResult(state=ToolCallState.FAILURE, message=msg)
        attached_entity_id = self.attached_entity.id
        self.attached_entity = None
        return ToolCallResult(state=ToolCallState.SUCCESS, message=f"Detach succeeded. `{attached_entity_id}` is no longer connected.")
