from typing import Any, Callable, ClassVar, Dict, Optional, List, Type, Optional
from pydantic import BaseModel
from simulation.ToolCall import ToolCallResult, ToolCallState, tool
from simulation.World import World, Simulation
from simulation.Entity import Location
from simulation.Component import Chassis, ComponentSlot, Component, ToolCall, PowerPack, SmallPowerPack, ComputerProbe
from random import randint

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

    # Can move to an entity by its type or by its ID
    #  If a type is provided, it will find the nearest entity of that type.
    #  If more than one entity matches and is equidistant, it will choose the first one found.
    @tool
    def move_to_entity(self, identifier: Type[Component] | str):
        """
        Move the chassis to the nearest entity of a specific type or by its ID.

        Args:
            world (World): The world in which the chassis is located.
            identifier (Type[Component] | str): The type of entity or its ID to move to.
        """

        world:World = self.chassis.world

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

    @tool
    def move_to_location(self, x: int, y: int):
        """
        Move the chassis to a specific location in the world.
        Args:
            world (World): The world in which the chassis is located.
            x (int): The x-coordinate of the destination.
            y (int): The y-coordinate of the destination.
        """
        # Set the destination of the chassis to the specified location
        self.destination = Location(x=x, y=y)
        # Calculate the path to the destination
        self.path_to_destination = self.find_path(self.chassis.location, self.destination)

    def find_path(self, start: Location, end: Location) -> List[Location]:
        # Overly simplistic pathfinding algorithm.
        path = []
        curr = start
        while curr != end:
            # Alternate randomly between moving in x or y direction
            x_first = randint(0, 1) == 0
            if x_first:
                if curr.x != end.x:
                    # Move in the x direction towards the end
                    curr = Location(x=curr.x + (1 if end.x > curr.x else -1), y=curr.y)
                elif curr.y != end.y:
                    # Move in the y direction towards the end
                    curr = Location(x=curr.x, y=curr.y + (1 if end.y > curr.y else -1))
            else:
                if curr.y != end.y:
                    # Move in the y direction towards the end
                    curr = Location(x=curr.x, y=curr.y + (1 if end.y > curr.y else -1))
                elif curr.x != end.x:
                    # Move in the x direction towards the end
                    curr = Location(x=curr.x + (1 if end.x > curr.x else -1), y=curr.y)

            # Add the current location to the path
            path.append(curr)
        return path

    def tick(self):
        self.info(f"Tick at location {self.chassis.location} with destination {self.destination}")
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
            self.info(f"Cooling down, {self.current_cooldown} ticks remaining.")
            return

        power:PowerPack = self.chassis.get_component(PowerPack)
        if not power:
            self.error(f"Cannot function without a power pack.")
            return

        if power.charge <= 0:
            self.warn(f"Power pack is empty. Cannot function without power!")
            return

        # TODO: Collision checking vs. the world map
        # Get the next location in the path to the destination
        if not self.path_to_destination:
            self.path_to_destination = self.find_path(self.chassis.location, self.destination)

        if not self.path_to_destination or len(self.path_to_destination) == 0:
            self.error(f"No path to destination found. Cannot move.")
            return
        
        # Peek at the next location in the path
        next_location = self.path_to_destination[0]
            
        # Check to ensure that we can navigate to the next location
        # TODO: Implement world collision checking
        #if not world.is_location_navigable(next_location):
        #    self.chassis.post_error(self, f"Next location {next_location} is not navigable. Cannot move.")
        #    self.path_to_destination = None
        #    self.destination = None
        #    return

        # Move to the next location
        self.chassis.location = next_location
        self.path_to_destination.pop(0)  # Remove the first location from the path

        # Consume power for movement
        power.charge -= 1  # Assuming each movement costs 1 unit of power

        # Wait for X ticks to cooldown after moving, but only if we have more things to in our path
        self.current_cooldown = self.cooldown_delay

class AStarMotivator(Motivator):
    name: str = "Advanced Motivator"

    def find_path(self, start: Location, end: Location) -> List[Location]:
        # A* pathfinding logic
        # TODO: Use the world's collision map to find a valid path
        return super().find_path(start, end)

# Chronometer is a component that allows droids to be aware of time.
#. For now, it only provides a single tool call to allow sleeping for a specified number of ticks.
class Chronometer(Component):
    name: str = "Chronometer"

    wake_time: int = 0 # The tick at which the droid will wake up

    @tool
    def sleep(self, ticks: int) -> Callable[[], ToolCallResult]:
        """
        Sleep for a specified number of ticks.
        Args:
            ticks (int): The number of ticks to sleep.
        """
        if ticks <= 0:
            raise ValueError("Ticks must be a positive integer.")
        self.info(f"Sleeping for {ticks} ticks.")
        self.wake_time = Simulation.tick_count + ticks

        return self.sleep_isdone

    def sleep_isdone(self) -> ToolCallResult:
        """
        Check if the sleep is done.
        Returns:
            ToolCallResult: The result of the tool call.
        """
        if Simulation.tick_count >= self.wake_time:
            return ToolCallResult(state=ToolCallState.SUCCESS)
        return ToolCallResult(state=ToolCallState.IN_PROCESS)
