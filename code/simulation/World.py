import asyncio
from time import sleep
from typing import Dict, List, Optional, Type
from pydantic import BaseModel

from simulation.Entity import Entity

# --- World System ---
class World(BaseModel):
    # TODO: Implement a map system to represent the world.
    #  At the very least, we need a grid collision map for checking movement.
    entities: Dict[str, Entity] = {}

    def __init__(self, **data):
        super().__init__(**data)

    def add_entity(self, entity: Entity):
        self.entities[entity.id] = entity

    def get_entity(self, identifier: Type[Entity] | str) -> Optional[Entity]:
        if isinstance(identifier, str):
            # Check for an entity with the given ID
            return self.entities.get(identifier, None)
        elif isinstance(identifier, type) and issubclass(identifier, Entity):
            # If a Type is provided, return the first entity of that type found
            for entity in self.entities.values():
                if isinstance(entity, identifier):
                    return entity
            return None
        else:
            # TODO: Raise this as an error that can be seen by any AI
            raise TypeError("Identifier must be a Type of Entity or a string representing an entity ID.")
        
    def get_entities(self, identifier: Type[Entity] | str) -> List[Optional[Entity]]:
        if isinstance(identifier, str):
            # Return a list of entities with the given ID
            return [self.entities.get(identifier, None)]
        elif isinstance(identifier, type) and issubclass(identifier, Entity):
            # If a Type is provided, return all entities of that type found
            return [entity for entity in self.entities.values() if isinstance(entity, identifier)]
        else:
            raise TypeError("Identifier must be a Type of Entity or a string representing an entity ID.")

    def tick(self):
        entities_are_thinking = False
        # Call the tick method on all entities in the world
        for entity in self.entities.values():
            entity.tick(self)
            if entity.is_thinking:
                entities_are_thinking = True

        return entities_are_thinking  # Return True if any entity is thinking, otherwise False
        
# --- Simulation System ---

# The Simulation is a high-level controller that manages the world and the simulation loop

class Simulation(BaseModel):
    world: World = World()

    running: bool = False  # Flag to control the simulation loop

    tick_count: int = 0  # Number of ticks that have occurred in the simulation

    simulation_delay: float = 0.5  # Delay between simulation ticks in seconds
    simulation_delay_max: float = 1.0 # What is the maximum delay between simulation ticks? If LLM-based entities are thinking, then wait this long before proceeding to the next tick. This gives the simulation a semblance of determinism even as it runs at variable speeds.

    simulation_task: Optional[asyncio.Task] = None  # Task for running the simulation loop

    event_bus: Optional[asyncio.Event] = None  # Event bus for sending and receiving events

    def __init__(self, **data):
        super().__init__(**data)

    def run(self, ticks: Optional[int] = None):
        # Start the simulation loop in a separate thread
        self.running = True

        if self.simulation_task and not self.simulation_task.done():
            print("Simulation is already running.")
            return self.simulation_task

        self.simulation_task = asyncio.create_task(self._do_run(ticks))

        return self.simulation_task
    
    def run_sync(self, ticks: Optional[int] = None):
        """Run the simulation synchronously for a specified number of ticks."""
        if self.simulation_task and not self.simulation_task.done():
            print("Simulation is already running.")
            return self.simulation_task

        # Run the simulation loop in a blocking manner
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._do_run(ticks))


    async def _do_run(self, ticks: Optional[int] = None):
        """Run the simulation asynchronously for a specified number of ticks."""
        self.running = True

        while self.running:
            self.tick_count += 1
            print(f"Simulation: Beginning tick {self.tick_count}")

            # Send on-before-tick event to the event bus
            if self.event_bus:
                await self.event_bus.send_event("on-before-tick", {"tick": self.tick_count})

            # Tick everything in the world
            entities_are_thinking = self.world.tick()

            sleep_time = self.simulation_delay
            if entities_are_thinking:
                # If no entities are thinking, then give them the maximum delay to think
                sleep_time = self.simulation_delay_max
                print(f"Simulation: Entities are thinking, sleeping for {sleep_time} seconds.")

            # Sleep for the specified delay before the next tick
            asyncio.sleep(sleep_time)

            print(f"Simulation: Finished tick {self.tick_count}")

            if ticks is not None and self.tick_count >= ticks:
                # If we have reached the number of ticks to run, stop the simulation
                self.running = False
                


    