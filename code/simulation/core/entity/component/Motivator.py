from typing import Any, Callable, Optional, List
from simulation.llm.ToolCall import ToolCallResult, ToolCallState, tool
from simulation.core.World import World
from simulation.core.entity.Entity import Location
from simulation.core.entity.component.Component import Component, PowerPack
from simulation.movement_intent import MovementIntent

# --- Droid Components ---
class Motivator(Component):
    name: str = "Basic Motivator"
    # Motivators are components that allow droids to move around the world.
    # They can be simple (like a basic movement system) or complex (like an A* pathfinding system).
    # Motivators can be installed in Chassis to provide movement capabilities.

    destination: Optional[Location] = None  # The destination the chassis is moving towards

    path_to_destination: Optional[List[Location]] = None  # The path to the destination
    cooldown_remaining: int = 0  # Cooldown for movement after each tick
    cooldown_delay: int = 1  # Delay in ticks between movements
    power_cost_per_step: int = 1  # Power cost for each movement step
    last_block_reason: Optional[str] = None

    deterministic_paths: bool = True  # for test stability

    # Can move to an entity by its type or by its ID
    #  If a type is provided, it will find the nearest entity of that type.
    #  If more than one entity matches and is equidistant, it will choose the first one found.
    @tool
    def move_to_entity(self, identifier: str) -> Callable[..., ToolCallResult]:
        """
        Move to the nearest entity of a specific type or by its ID.

        Args:
            identifier (str): The type of entity or its ID to move to.
        """

        world: World = self.chassis.world

        # Find the entity by ID and set the destination to its location
        entities = world.get_entities(identifier)

        if len(entities) == 0:
            raise ValueError(f"No entities found with identifier `{identifier}`.")
        
        # Sort entities by distance to the chassis
        entities.sort(key=lambda e: self.chassis.location.distance_to(e.location))

        entity = entities[0]  # Get the closest entity

        # Assign our desination to the entity's location
        self.destination = entity.location

        # Calculate the path to the destination
        self.path_to_destination = self.find_path(self.chassis.location, self.destination)

        return ToolCallResult(state=ToolCallState.IN_PROCESS, callback=self.move_to_isdone)

    @tool
    def move_to_location(self, x: int, y: int) -> Callable[..., ToolCallResult]:
        """
        Move to a specific location in the world.
        Args:
            x (int): The x-coordinate of the destination.
            y (int): The y-coordinate of the destination.
        """
        # Set the destination of the chassis to the specified location
        self.destination = Location(x=x, y=y)
        # Calculate the path to the destination
        self.path_to_destination = self.find_path(self.chassis.location, self.destination)
        return ToolCallResult(state=ToolCallState.IN_PROCESS, callback=self.move_to_isdone)

    def move_to_isdone(self) -> ToolCallResult:
        """
        Check if the chassis has reached its destination.
        Returns:
            ToolCallResult: The result of the tool call.
        """
        if self.chassis.location == self.destination or self.destination is None:
            return ToolCallResult(state=ToolCallState.SUCCESS, message=f"Arrived at destination {self.chassis.location}.")
        return ToolCallResult(state=ToolCallState.IN_PROCESS)

    def find_path(self, start: Location, end: Location) -> List[Location]:
        """Build a simple greedy Manhattan path.

        Enhancement: If the destination Y is negative (above the map border),
        prioritize vertical movement first so we exit the map bounds quickly
        instead of being blocked by the top border while trying horizontal
        movement. This supports tests that move to negative Y coordinates.
        """
        path: List[Location] = []
        curr = start
        vertical_first = self.deterministic_paths and end.y < 0
        while curr != end:
            if self.deterministic_paths:
                if vertical_first:
                    if curr.y != end.y:
                        curr = Location(x=curr.x, y=curr.y + (1 if end.y > curr.y else -1))
                    elif curr.x != end.x:
                        curr = Location(x=curr.x + (1 if end.x > curr.x else -1), y=curr.y)
                else:
                    if curr.x != end.x:
                        curr = Location(x=curr.x + (1 if end.x > curr.x else -1), y=curr.y)
                    elif curr.y != end.y:
                        curr = Location(x=curr.x, y=curr.y + (1 if end.y > curr.y else -1))
            else:
                from random import randint
                x_first = randint(0, 1) == 0 and not vertical_first
                if x_first:
                    if curr.x != end.x:
                        curr = Location(x=curr.x + (1 if end.x > curr.x else -1), y=curr.y)
                    elif curr.y != end.y:
                        curr = Location(x=curr.x, y=curr.y + (1 if end.y > curr.y else -1))
                else:
                    if curr.y != end.y:
                        curr = Location(x=curr.x, y=curr.y + (1 if end.y > curr.y else -1))
                    elif curr.x != end.x:
                        curr = Location(x=curr.x + (1 if end.x > curr.x else -1), y=curr.y)
            path.append(curr)
        return path

    @property
    def current_cooldown(self) -> int:
        return self.cooldown_remaining

    @current_cooldown.setter
    def current_cooldown(self, v: int):
        self.cooldown_remaining = max(0, v)

    def tick(self):
        if self.destination is None or self.chassis.location == self.destination:
            # We have arrived at our destination, so clear the destination
            self.destination = None
            self.path_to_destination = None
            self.cooldown_remaining = 0
            return
        
        if self.cooldown_remaining > 0:
            # We are currently cooling down, so do nothing for this tick
            self.cooldown_remaining -= 1
            self.last_block_reason = 'cooldown'
            return

        power: PowerPack = self.chassis.get_component(PowerPack)  # type: ignore
        if not power:
            self.error("Cannot function without a power pack.")
            return

        if power.charge < self.power_cost_per_step:
            self.last_block_reason = "no_power"
            self.warn("Insufficient power to issue movement intent.")
            return

        if not self.path_to_destination:
            self.path_to_destination = self.find_path(self.chassis.location, self.destination)

        if not self.path_to_destination:
            self.warn("No path available to destination.")
            self.destination = None
            return
        
        # Peek at the next location in the path
        next_location = self.path_to_destination[0]
            
        # Calculate the movement deltas
        dx = next_location.x - self.chassis.location.x
        dy = next_location.y - self.chassis.location.y

        remaining = len(self.path_to_destination)
        issued = self.chassis.request_move(dx, dy, source="Motivator", remaining_path=remaining)
        if not issued:
            self.last_block_reason = "intent_exists"
            return

    # Callbacks from Chassis/world
    def on_move_applied(self, old_loc: Location, new_loc: Location, intent: MovementIntent):
        power: PowerPack = self.chassis.get_component(PowerPack)  # type: ignore
        if power:
            power.charge = max(0, power.charge - self.power_cost_per_step)
        if self.path_to_destination and len(self.path_to_destination) > 0 and self.path_to_destination[0] == new_loc:
            self.path_to_destination.pop(0)
        if not self.path_to_destination:
            self.destination = None
        self.cooldown_remaining = self.cooldown_delay
        self.last_block_reason = None

    def on_move_blocked(self, intent: MovementIntent, reason: str, blocker: Any | None = None):
        self.last_block_reason = reason
        self.info(f"Move blocked: reason={reason} intent=({intent.dx},{intent.dy}) blocker={getattr(blocker, 'id', None)}")
        if self.path_to_destination and reason in ("OCCUPIED", "BLOCKED_TILE"):
            self.path_to_destination.clear()

class AStarMotivator(Motivator):
    name: str = "Advanced Motivator"

    def find_path(self, start: Location, end: Location) -> List[Location]:
        # A* pathfinding logic
        # TODO: Use the world's collision map to find a valid path
        return super().find_path(start, end)

Motivator.model_rebuild()
