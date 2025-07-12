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

    # HACK: Should eventually maybe think of a better way to handle this.
    entity_thinking_count: int = 0  # Count of how many entities are currently thinking

    def __init__(self, **data):
        super().__init__(**data)

    def add_entity(self, entity: Entity):
        entity.world = self  # Set the world reference in the entity
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
        
    def get_entities(self, identifier: Type[Entity] | str) -> List[Entity]:
        if isinstance(identifier, str):
            # Return a list of entities with the given ID
            return [self.entities.get(identifier, None)]
        elif isinstance(identifier, type) and issubclass(identifier, Entity):
            # If a Type is provided, return all Entities found of that type
            return [entity for entity in self.entities.values() if isinstance(entity, identifier)]
        else:
            raise TypeError("Identifier must be a Type of Entity or a string representing an entity ID.")

    def tick(self):
        # Call the tick method on all entities in the world
        for entity in self.entities.values():
            entity.tick()
        # No broadcast here; handled by Simulation

    def to_json(self):
        return {
            "entities": {eid: entity.to_json() for eid, entity in self.entities.items()}
        }

# --- Simulation System ---

# The Simulation is a high-level controller that manages the world and the simulation loop

class Simulation(BaseModel):
    running: bool = False  # Flag to control the simulation loop

    tick_count: int = 0  # Number of ticks that have occurred in the simulation

    simulation_delay: float = 0.1  # Delay between simulation ticks in seconds
    simulation_delay_max: float = 0.5 # What is the maximum delay between simulation ticks? If LLM-based entities are thinking, then wait this long before proceeding to the next tick. This gives the simulation a semblance of determinism even as it runs at variable speeds.

    log_level: int = 0  # Log level for the simulation (0 = info, 1 = warning, 2 = error)

    # TODO: Make this more easily configurable -- possibly with a dictionary of endpoints for different model names or services.
    llm_url: str = "http://localhost:8080/v1/chat/completions"  # URL for the LLM endpoint

    world: World = World()  # The world that the simulation is running in

    _on_tick_subscribers: List = []  # List of callback functions to call after each tick

    # Singleton pattern to ensure only one instance of Simulation exists
    __instance: Optional['Simulation'] = None
    @classmethod
    def get_instance(cls) -> 'Simulation':
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def run(self, ticks: Optional[int] = None):
        # Start the simulation loop in a separate thread
        simulation_task = asyncio.create_task(self._do_run(ticks))

        return simulation_task
    
    def run_sync(self, ticks: Optional[int] = None):
        """Run the simulation synchronously for a specified number of ticks."""
        # Run the simulation loop in a blocking manner
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._do_run(ticks))

    def subscribe_on_tick(self, callback):
        if callback not in self._on_tick_subscribers:
            self._on_tick_subscribers.append(callback)

    def unsubscribe_on_tick(self, callback):
        if callback in self._on_tick_subscribers:
            self._on_tick_subscribers.remove(callback)

    async def _do_run(self, ticks: Optional[int] = None):
        """Run the simulation asynchronously for a specified number of ticks."""
        self.running = True
        count = 0

        while self.running:
            self.world.tick()
            self.tick_count += 1
            count += 1
            # Call all on_tick subscribers
            for cb in self._on_tick_subscribers:
                try:
                    cb(self)
                except Exception as e:
                    print(f"[WARN] on_tick subscriber error: {e}")

            broadcast_game_state(self.world.to_json())

            if ticks is not None and count >= ticks:
                self.running = False
                break

            sleep_time = self.simulation_delay

            # Check to see if any agents are thinking
            if self.world.entity_thinking_count > 0:
                # If any entities are thinking, then give them the maximum delay to think
                sleep_time = self.simulation_delay_max
                print(f"Simulation: {self.world.entity_thinking_count} entities are thinking, sleeping for {sleep_time} seconds.")

            # Sleep for the specified delay before the next tick
            await asyncio.sleep(sleep_time)


