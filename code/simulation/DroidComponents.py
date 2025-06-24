from typing import ClassVar, Dict, Optional, List, Type, Optional
from pydantic import BaseModel
from simulation.World import World
from simulation.Entity import Location
from simulation.Component import Chassis, ComponentSlot, Component, ToolCall, PowerPack, SmallPowerPack, ComputerProbe

# --- Droid Components ---
class Motivator(Component):
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
    
    def move_to_location(self, world: World, x: int, y: int):
        # Set the destination of the chassis to the specified location
        self.chassis.destination = Location(x=x, y=y)

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

        # Assign our desgination to the entity's location
        self.chassis.destination = entity.location

    def on_tick(self, world: World):
        if self.chassis.destination == self.chassis.location:
            # If the destination is the same as the current location, do nothing
            return

        power = self.chassis.get_component(PowerPack)
        if not power:
            print("No power pack found in the chassis. CondenserUnit cannot function without a power pack.")
            # TODO: Post an error message that the AI can see
            return

        if power.charge <= 0:
            print("Power pack is empty. Cannot move without power!")
            # TODO: Post an error message to world and/or chassis system?
            return

        # TODO: Collision checking vs. the world map

        curr = self.chassis.location
        dest = self.chassis.destination
        dx = dest.x - curr.x
        dy = dest.y - curr.y
        if dx != 0:
            curr.x += 1 if dx > 0 else -1
            power.charge -= 1  # Consume power for movement
        elif dy != 0:
            curr.y += 1 if dy > 0 else -1
            power.charge -= 1  # Consume power for movement
        else:
            self.chassis.destination = None
            # TODO: Once we reach our destination, this tool call is done

class AStarMotivator(Motivator):
    def provides_tools(self) -> List[ToolCall]:
        return [
            ToolCall(
                function=self.move_to_location,
                description="Intelligently move to a specific location on the farm.",
                parameters={
                    "x": "The x coordinate to move to.",
                    "y": "The y coordinate to move to."
                }
            ),
            ToolCall(
                function=self.move_to_entity,
                description="Intelligently move to the nearest entity of a specific type or by its ID.",
                parameters={
                    "identifier": "The type of entity or its ID to move to."
                }
            )
        ]
    
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

    def on_tick(self, world: World):
        # Use A* pathfinding to move towards the destination
        # TODO: Implement collision checking vs. the world map
        # TODO: Implement A*
        if self.chassis and self.chassis.destination:
            # TODO: Cache the path as long as the destination has not changed
            path = self.find_path(world, self.chassis.location, self.chassis.destination)
            if path:
                next_location = path[0]
                self.chassis.location = next_location
                if next_location == self.chassis.destination:
                    self.chassis.destination = None

class DroidPersonality(Component):
    # Personalities are how droids interact with the world.
    #  This is an agentic AI that can be configured to perform tasks.
    # For actual implementations, see DroidPersonality.py
    pass
