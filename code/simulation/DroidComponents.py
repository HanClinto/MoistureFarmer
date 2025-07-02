from typing import Any, Callable, ClassVar, Dict, Optional, List, Type, Optional
from pydantic import BaseModel
from simulation.World import World
from simulation.Entity import Location
from simulation.Component import Chassis, ComponentSlot, Component, ToolCall, PowerPack, SmallPowerPack, ComputerProbe

# --- Droid Components ---
class Motivator(Component):
    name: str = "Basic Motivator"
    # Motivators are components that allow droids to move around the world.
    # They can be simple (like a basic movement system) or complex (like an A* pathfinding system).
    # Motivators can be installed in Chassis to provide movement capabilities.

    destination: Optional[Location] = None  # The destination the chassis is moving towards

    path_to_destination: Optional[List[Location]] = None  # The path to the destination
    current_cooldown: int = 0  # Cooldown for movement after each tick
    cooldown_delay: int = 1  # Delay in ticks between movements

    def provides_tools(self) -> List[ToolCall]:
        return [
            ToolCall(
                function=self.move_to_location,
                description="Move to a specific location on the farm.",
                parameters={
                    "x": "The x coordinate to move to.",
                    "y": "The y coordinate to move to."
                }
            ),
            ToolCall(
                function=self.move_to_entity,
                description="Move to the nearest entity of a specific type or by its ID.",
                parameters={
                    "identifier": "The type of entity or its ID to move to."
                }
            )
        ]

    # Can move to an entity by its type or by its ID
    #  If a type is provided, it will find the nearest entity of that type.
    #  If more than one entity matches and is equidistant, it will choose the first one found.
    def move_to_entity(self, world: World, identifier: Type[Component] | str):
        # Find the entity by ID and set the destination to its location
        entities = world.get_entities(identifier)

        if len(entities) == 0:
            print(f"No entities found with identifier {identifier}.")
            return
        
        # Sort entities by distance to the chassis
        entities.sort(key=lambda e: self.chassis.location.distance_to(e.location))

        entity = entities[0]  # Get the closest entity

        # Assign our desination to the entity's location
        self.destination = entity.location


    def find_path(self, world: World, start: Location, end: Location) -> List[Location]:
        # Placeholder for A* pathfinding logic
        path = []
        curr = start
        while curr != end:
            if curr.x < end.x:
                curr = Location(x=curr.x + 1, y=curr.y)
            elif curr.x > end.x:
                curr = Location(x=curr.x - 1, y=curr.y)
            elif curr.y < end.y:
                curr = Location(x=curr.x, y=curr.y + 1)
            elif curr.y > end.y:
                curr = Location(x=curr.x, y=curr.y - 1)
            path.append(curr)
        return path

    def move_to_location(self, world: World, x: int, y: int):
        # Set the destination of the chassis to the specified location
        self.destination = Location(x=x, y=y)
        # Calculate the path to the destination
        self.path_to_destination = self.find_path(world, self.chassis.location, self.destination)


    def tick(self, world: World):
        if self.chassis.location == self.destination:
            # We have arrived at our destination, so clear the destination
            self.destination = None
            self.current_cooldown = 0  # Reset cooldown after arriving
            # If the destination is the same as the current location, do nothing
            # TODO: Announce event that we have arrived (?)
            return
        
        if self.current_cooldown > 0:
            # We are currently cooling down, so do nothing for this tick
            self.current_cooldown -= 1
            return

        power = self.chassis.get_component(PowerPack)
        if not power:
            self.chassis.post_error(self, f"No power pack found in the chassis. Cannot function without a power pack.")
            return

        if power.charge <= 0:
            self.chassis.post_error(self, "Power pack is empty. Cannot function without power!")
            return

        # TODO: Collision checking vs. the world map
        # Get the next location in the path to the destination
        if not self.path_to_destination:
            self.path_to_destination = self.find_path(world, self.chassis.location, self.destination)

        if not self.path_to_destination or len(self.path_to_destination) == 0:
            self.chassis.post_error(self, "No path to destination found. Cannot move.")
            return
        
        # Peek at the next location in the path
        next_location = self.path_to_destination[0]
            
        # Check to ensure that we can navigate to the next location
        if not world.is_location_navigable(next_location):
            self.chassis.post_error(self, f"Next location {next_location} is not navigable. Cannot move.")
            self.path_to_destination = None
            self.destination = None
            return

        # Move to the next location
        self.chassis.location = next_location
        self.path_to_destination.pop(0)  # Remove the first location from the path

        # Consume power for movement
        power.charge -= 1  # Assuming each movement costs 1 unit of power

        # Wait for X ticks to cooldown after moving, but only if we have more things to in our path
        self.current_cooldown = self.cooldown_delay

class AStarMotivator(Motivator):
    name: str = "Advanced Motivator"

    def find_path(self, world: World, start: Location, end: Location) -> List[Location]:
        # Placeholder for A* pathfinding logic
        path = []
        curr = start
        while curr != end:
            if curr.x < end.x:
                curr = Location(x=curr.x + 1, y=curr.y)
            elif curr.x > end.x:
                curr = Location(x=curr.x - 1, y=curr.y)
            elif curr.y < end.y:
                curr = Location(x=curr.x, y=curr.y + 1)
            elif curr.y > end.y:
                curr = Location(x=curr.x, y=curr.y - 1)
            path.append(curr)
        return path
