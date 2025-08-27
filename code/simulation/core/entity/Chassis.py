import inspect
import logging
from typing import TYPE_CHECKING, TypeVar, overload, ClassVar, Dict, Optional, List, Type, Any
from simulation.core.entity.Entity import Entity, Location, GameObject, LogMessage
from simulation.core.entity.component.Component import Component
from simulation.llm.ToolCall import ToolCall, _IS_TOOL_FUNCTION
from simulation.movement_intent import MovementIntent

if TYPE_CHECKING:
    from simulation.core.entity.ComponentSlot import \
        ComponentSlot  # type: ignore

T = TypeVar('T', bound=Component)

# -- Chassis System ---
# Chassis are the physical bodies of entities that can have components
#  installed in them to extend their capabilities.
# Chassis can be droids, equipment (such as vaporators), or anything
#  that would need to be repaired, upgraded, run-down, or otherwise
#  interacted with in the game world.
# If an Entity does not need to be repaired or upgraded or have modular
#  capabilities, then it does not need a Chassis, and can be an Entity
#  directly.
# Chassis have slots for Components, which can be installed or removed.
# Different Chassis will have different Slots that accept different
#  types of Components.
# Components add funcionality to the Chassis, such as movement, power,
#  or other capabilities. Some of these capabilities will be exposed to
#  the agentic AI as functions that can be called in the form of tools,
#  such as moving to a location, charging equipment, or recharging itself.

class Chassis(Entity):
    slots: Dict[str, 'ComponentSlot']
    health: int = 100
    # Movement extension fields
    footprint_w: int = 1
    footprint_h: int = 1
    move_priority: int = 100
    pending_intent: Optional[MovementIntent] = None

    @property
    def components(self):  # convenience iterable of installed components
        return [slot.component for slot in self.slots.values() if slot.component]

    def __init__(__pydantic_self__, **data):
        super().__init__(**data)
        # Ensure every component is properly installed in its slot
        for slot_id, slot in __pydantic_self__.slots.items():
            slot.slot_id = slot.slot_id or slot_id
            if slot.component:
                __pydantic_self__.install_component(slot.slot_id, slot.component)

    def install_component(self, slot_id: str, component: Component):
        if slot_id not in self.slots:
            # TODO: Don't raise a ValueError for this, but instead post an error message to the world and/or chassis system
            raise ValueError(f"Slot '{slot_id}' not defined.")
        slot = self.slots[slot_id]
        if not isinstance(component, slot.accepts):
            # TODO: Don't raise a TypeError for this, but instead post an error message to the world and/or chassis system
            raise TypeError(f"Component '{component.id}' is not a valid type for slot '{slot_id}'. Expected {slot.accepts.__name__} or compatible subclass.")
        component.chassis = self
        slot.component = component
        # Raise an on_installed event for the component so that it can initialize itself (if needed)
        component.on_installed(self)

    @overload
    def get_component(self, identifier: Type[T]) -> Optional[T]: ...
    @overload
    def get_component(self, identifier: str) -> Optional[Component]: ...

    # get_component accepts a Type or string parameter.
    #  If a Type is provided, it will return the first component of that type found in the slots.
    #  If a string is provided, it will return the component of the Slot with an ID matching that ID.
    #  If no Slot with that ID exists, it will then return the first Component whose ID matches that identifier.
    #  If no Component with that ID exists, then it will return the first Component whose class or parent class name matches that identifier.
    #  If no matching Component or Slot is found, then it will return None.
    def get_component(self, identifier: Type[Component] | str) -> Optional[Component]:
        if isinstance(identifier, str):
            # Check for a slot with the given ID first
            if identifier in self.slots:
                return self.slots[identifier].component
            # If no slot found, check all components for a matching ID
            for slot in self.slots.values():
                if slot.component and slot.component.id == identifier:
                    return slot.component
            # If no ID found, check all components for a matching type
            for slot in self.slots.values():
                if slot.component:
                    # Check the __class__.__name__ and all parent class names
                    if slot.component.__class__.__name__ == identifier:
                        return slot.component
                    for base in inspect.getmro(slot.component.__class__):
                        if base.__name__ == identifier:
                            return slot.component
            return None
        elif isinstance(identifier, type) and issubclass(identifier, Component):
            # If a Type is provided, return the first component of that type found in the slots
            for slot in self.slots.values():
                if isinstance(slot.component, identifier):
                    return slot.component
            return None
        else:
            raise TypeError("Identifier must be a Type of Component or a string representing a slot ID or component ID.")

    def get_available_tools(self) -> Dict[str, ToolCall]:
        # Collect all tool calls from all components in the chassis
        all_tools = {}
        for slot in self.slots.values():
            if slot.component:
                tools = slot.component.provides_tools()
                for tool_name, tool_call in tools.items():
                    if tool_name not in all_tools:
                        all_tools[tool_name] = tool_call
                    else:
                        # If a tool with the same name already exists, we can either skip or somehow denote which component they come from.
                        # Here we choose to skip and give preference to the first one found.
                        self.warn(f"Tool '{tool_name}' already exists in {self.id}. Skipping duplicate.")

        return all_tools
    
    def get_logs(self) -> List[LogMessage]:
        """Get the log history for this chassis and all components, sorted by timestamp."""
        logs = super().get_logs()
        for slot in self.slots.values():
            if slot.component:
                logs.extend(slot.component.get_logs())
        # Sort logs by timestamp
        logs.sort(key=lambda log: log.timestamp)  # Sort by timestamp
        return logs
    
    def tick(self):
        for slot in self.slots.values():
            if slot.component:
                slot.component.tick()

    def to_json(self, short: bool = False):
        data = {
            **super().to_json(short),
        }
        data["health"] = getattr(self, "health", None)
        # Serialize slots and their components
        data["slots"] = {
            slot_id: {
                "accepts": slot.accepts.__name__,
                "component": slot.component.to_json(short) if slot.component else None
            } for slot_id, slot in self.slots.items()
        }
        return data

    # Movement API
    def request_move(self, dx: int, dy: int, **metadata) -> bool:
        if self.pending_intent is not None:
            self.warn(f"Chassis {self.id} already has a pending intent; ignoring new request.")
            return False
        intent = MovementIntent(dx=dx, dy=dy, metadata=metadata)
        invalid = intent.validate()
        if invalid:
            self.warn(f"Invalid movement intent ({dx},{dy}) rejected: {invalid}")
            return False
        self.pending_intent = intent
        return True

    def clear_intent(self):
        self.pending_intent = None

    def occupied_tiles(self, at_location: Location | None = None):
        loc = at_location or self.location
        for oy in range(self.footprint_h):
            for ox in range(self.footprint_w):
                yield (loc.x + ox, loc.y + oy)

    # Callback dispatchers (Motivator or others may override by component methods)
    def on_move_applied(self, old_loc: Location, new_loc: Location, intent: MovementIntent):
        motivator = self.get_component_by_type_name("Motivator")
        if motivator and hasattr(motivator, "on_move_applied"):
            try:
                motivator.on_move_applied(old_loc, new_loc, intent)
            except Exception as e:
                self.error(f"on_move_applied error: {e}")

    def on_move_blocked(self, intent: MovementIntent, reason: str, blocker: Any | None = None):
        for comp in self.components:
            if hasattr(comp, 'on_move_blocked'):
                try:
                    comp.on_move_blocked(intent, reason, blocker)
                except Exception:
                    logging.exception("Component on_move_blocked error")

    # Helper to locate component by class name (without importing class directly)
    def get_component_by_type_name(self, type_name: str):
        for slot in self.slots.values():
            comp = slot.component
            if comp:
                # Check the __class__.__name__ and all parent class names
                if comp.__class__.__name__ == type_name:
                    return comp
                for base in inspect.getmro(comp.__class__):
                    if base.__name__ == type_name:
                        return comp
        return None

