from datetime import datetime
import inspect
from typing import ClassVar, Dict, Optional, List, Tuple, Type, Callable, Any
from pydantic import BaseModel
from simulation.Entity import Entity, Location, GameObject, LogMessage
from simulation.World import World
from simulation.ToolCall import ToolCall, _IS_TOOL_FUNCTION

# --- Component System ---
# Components are modular parts that can be installed in Chassis to
#  extend their capabilities. They can provide functionality such as
#  movement, power, or other capabilities. Components can be installed,
#  removed, and upgraded in Chassis. They can also be repaired or
#  adjusted to improve their performance or extend their lifespan.
# If an Agentic AI needs to interact with a Component, it will do so
#  through the Chassis that contains the Component, rather than directly
#  interacting with the Component itself. This allows for a more
#  modular and flexible system where Components can be swapped out or
#  upgraded without affecting the AI's interaction with the Chassis.
# Components provide functionality to Agentic AI in the form of functions
#  that can be called as tools, such as moving to a location, charging
#  equipment, or recharging itself. These functions are defined in the
#  `provides` method of the Component class and its subclasses.

class Component(GameObject):
    name: Optional[str] = None
    description: Optional[str] = None
    durability: int = 100
    chassis: Optional['Chassis'] = None

    def tick(self):
        pass

    def provides_tools(self) -> Dict[str, ToolCall]:
        # Find all methods (including inherited) marked as tool functions
        tool_methods = {}
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if getattr(method, _IS_TOOL_FUNCTION, False):
                tool_methods[name] = ToolCall(method)
        return tool_methods

    def on_installed(self, chassis: 'Chassis'):
        # This method can be overridden by subclasses to perform initialization logic when the component is installed in a chassis
        self.info(f"Component {self.id} installed in chassis {chassis.id}.")

    def to_json(self):
        props = self.model_dump(
                exclude_defaults=False,
                exclude_none=False,
                exclude={'chassis', 'world', 'entity'}  # Exclude back-references
            )
        props['type'] = self.__class__.__name__
        return props

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
    model: str
    slots: Dict[str, 'ComponentSlot']
    health: int = 100

    def __init__(__pydantic_self__, **data):
        super().__init__(**data)
        # Ensure every component is properly installed in its slot
        for slot_id, slot in __pydantic_self__.slots.items():
            # Or a more Pythonic way to do this:
            slot.slot_id = slot.slot_id or slot_id
            # If there is a default component for the slot, install it.
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

    # get_component accepts a Type or string parameter.
    #  If a Type is provided, it will return the first component of that type found in the slots.
    #  If a string is provided, it will return the component of the Slot with an ID matching that ID.
    #  If no Slot with that ID exists, it will then return the first component matching that ID from any slot.
    #.  If no matching Component or Slot is found, then it will return None.
    def get_component(self, identifier: Type[Component] | str) -> Optional[Component]:
        if isinstance(identifier, str):
            # Check for a slot with the given ID first
            if identifier in self.slots:
                return self.slots[identifier].component
            # If no slot found, check all components for a matching ID
            for slot in self.slots.values():
                if slot.component and slot.component.id == identifier:
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

    def to_json(self):
        data = super().to_json()
        data["model"] = getattr(self, "model", None)
        data["health"] = getattr(self, "health", None)
        # Serialize slots and their components
        data["slots"] = {
            slot_id: {
                "accepts": slot.accepts.__name__,
                "component": slot.component.to_json() if slot.component else None
            } for slot_id, slot in self.slots.items()
        }
        return data

class ComponentSlot(BaseModel):
    slot_id: Optional[str] = None
    accepts: Type[Component]
    component: Optional[Component] = None


# --- Specific Component Systems ---
class PowerPack(Component):
    charge_max: int = 100
    charge: int = 100

class SmallPowerPack(PowerPack):
    charge_max: int = 50
    charge: int = 50

class LargePowerPack(PowerPack):
    charge_max: int = 200
    charge: int = 200

class ComputerProbe(Component):
    pass
    #def provides(self):
    #    return ["connect_to_device", "download_status", "program"]

