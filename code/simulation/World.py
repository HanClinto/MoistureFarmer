import asyncio
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

    async def tick(self):
        # Run all entity ticks concurrently
        await asyncio.gather(*(entity.tick(self) for entity in self.entities.values()))
        
# --- Simulation System ---

# The Simulation is a high-level controller that manages the world and the simulation loop

class Simulation(BaseModel):
    world: World = World()

    running: bool = False  # Flag to control the simulation loop

    paused: bool = False  # Flag to pause the simulation
    tick_count: int = 0  # Number of ticks that have occurred in the simulation

    simulation_delay: float = 0.5  # Delay between simulation ticks in seconds
    simulation_delay_max: float = 1.0 # What is the maximum delay between simulation ticks? If LLM-based entities are thinking, then wait this long before proceeding to the next tick. This gives the simulation a semblance of determinism even as it runs at variable speeds.

    def __init__(self, **data):
        super().__init__(**data)

    def set_running(self, running: bool):
        """Set the simulation running state"""
        do_start_run = not self.running and running

        self.running = running

        if do_start_run:
            # If we are starting the simulation, we should start the run loop
            asyncio.create_task(self.run())

    async def run(self, ticks: Optional[int] = None):
        self.running = True

        while self.running:
            if not self.paused:
                entities_are_thinking = await self.world.tick()
                if entities_are_thinking:
                    # If no entities are thinking, then give them the maximum delay to think
                    await asyncio.sleep(self.simulation_delay_max)
                else:
                    # If entities are not thinking, then run as fast as the user wants us to.
                    await asyncio.sleep(self.simulation_delay)

                self.tick_count += 1
                if ticks is not None and self.tick_count >= ticks:
                    # If we have reached the number of ticks to run, stop the simulation
                    self.running = False
            else:
                # await for a trigger to resume the simulation
                # TODO: Implement a more sophisticated pause / resume mechanism so that we don't just busy-wait
                await asyncio.sleep(0.1)
                


    