import inspect
import logging
from typing import TYPE_CHECKING, TypeVar, overload, ClassVar, Dict, Optional, List, Type, Any
from simulation.core.entity.Entity import Entity, Location, GameObject, LogMessage
from simulation.llm.ToolCall import ToolCall, _IS_TOOL_FUNCTION
from simulation.movement_intent import MovementIntent

if TYPE_CHECKING:
    from simulation.core.entity.Chassis import Chassis  # type: ignore

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

    def to_json(self, short: bool = False):
        excludes_list = {'chassis',
                         'world',
                         'entity',
                         'pending_tool_call',
                         'pending_tool_completion_callback',
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
        return props
