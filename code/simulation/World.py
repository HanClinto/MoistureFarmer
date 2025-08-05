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

    def clear_entities(self):
        """Clear all entities from the world."""
        self.entities.clear()
        self.entity_thinking_count = 0

    def remove_entity(self, entity: Entity):
        """Remove an entity from the world."""
        if entity.id in self.entities:
            del self.entities[entity.id]
            if entity.thinking:
                self.entity_thinking_count -= 1

    def remove_entity_by_id(self, entity_id: str):
        """Remove an entity by its ID."""
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            if entity.thinking:
                self.entity_thinking_count -= 1
            del self.entities[entity_id]

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
        
    def get_entities(self, identifier: str) -> List[Entity]:
        matching_entities = [
            entity for entity in self.entities.values()
            if entity.id == identifier or entity.__class__.__name__ == identifier
            ]

        return matching_entities

    def tick(self):
        # Call the tick method on all entities in the world
        for entity in self.entities.values():
            entity.tick()
        # No broadcast here; handled by Simulation

    def to_json(self, short: bool = False):
        val = {
            "entities": {eid: entity.to_json(short) for eid, entity in self.entities.items()},
        }

        if not short:
            val["entity_thinking_count"] = self.entity_thinking_count

        return val
    
    def get_state_llm(self):
        return self.to_json(short=True)

# --- Simulation System ---

# The Simulation is a high-level controller that manages the world and the simulation loop
class Simulation(BaseModel):
    running: bool = False  # Flag to control the simulation loop
    paused: bool = False  # Flag to pause the simulation
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
    def get_instance(cls, **data) -> 'Simulation':
        if not cls.__instance is None:
            return cls.__instance
        return cls(**data)
    
    def __init__(self, **data):
        super().__init__(**data)
        # Ensure the world is initialized
        if not self.world:
            self.world = World(**data.get('world', {}))
            
        Simulation.__instance = self  # Set the singleton instance

    def to_json(self):
        """Convert the simulation state to JSON format."""
        return {
            "running": self.running,
            "paused": self.paused,
            "llm_url": self.llm_url,
            "tick_count": self.tick_count,
            "simulation_delay": self.simulation_delay,
            "simulation_delay_max": self.simulation_delay_max,
            "log_level": self.log_level,
            "world": self.world.to_json(),
        }

    def run(self, ticks: Optional[int] = None):
        # Start the simulation loop in a separate thread
        simulation_task = asyncio.create_task(self._do_run(ticks))

        return simulation_task
    
    def run_sync(self, ticks: Optional[int] = None):
        """Run the simulation synchronously for a specified number of ticks."""

        # Run the simulation loop in a blocking manner
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError as e:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self._do_run(ticks))

    def subscribe_on_tick(self, callback):
        if callback not in self._on_tick_subscribers:
            self._on_tick_subscribers.append(callback)

    def unsubscribe_on_tick(self, callback):
        if callback in self._on_tick_subscribers:
            self._on_tick_subscribers.remove(callback)

    def dispatch_on_tick(self):
        """Call all on_tick subscribers."""
        for cb in self._on_tick_subscribers:
            try:
                cb(self)
            except Exception as e:
                print(f"[WARN] on_tick subscriber error: {e}")

    async def _do_run(self, ticks: Optional[int] = None):
        """Run the simulation asynchronously for a specified number of ticks."""
        self.running = True
        count = 0

        while self.running:
            sleep_time = 0.1

            if not self.paused:
                # Reset the thinking count at the start of each tick
                self.world.entity_thinking_count = 0

                # Advance the world by one tick
                self.world.tick()
                self.tick_count += 1
                count += 1
                # Call all on_tick subscribers
                for cb in self._on_tick_subscribers:
                    try:
                        cb(self)
                    except Exception as e:
                        print(f"[WARN] on_tick subscriber error: {e}")

                self.dispatch_on_tick()

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


