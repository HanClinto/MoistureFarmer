import asyncio
from time import sleep
from typing import Dict, List, Optional, Type
from pydantic import BaseModel

from simulation.Entity import Entity, Location
from simulation.Tilemap import Tilemap
from simulation.TileMapEntity import TileMapEntity

# --- World System ---
class World(BaseModel):
    # TODO: Implement a map system to represent the world.
    #  At the very least, we need a grid collision map for checking movement.
    entities: Dict[str, Entity] = {}
    # Maintain insertion order list for TileMapEntity movement. Entities can have a priority attribute.
    _movement_insertion_order: List[str] = []
    # Last movement journal (list of dict entries)
    last_movement_journal: List[Dict] = []

    # HACK: Should eventually maybe think of a better way to handle this.
    entity_thinking_count: int = 0  # Count of how many entities are currently thinking
    # Extracted tilemap object (mock implementation)
    tilemap: Optional[Tilemap] = None

    def __init__(self, **data):
        super().__init__(**data)

    def add_entity(self, entity: Entity):
        entity.world = self  # Set the world reference in the entity
        self.entities[entity.id] = entity
        if isinstance(entity, TileMapEntity):
            # Append if not already present
            if entity.id not in self._movement_insertion_order:
                self._movement_insertion_order.append(entity.id)

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
            if entity.id in self._movement_insertion_order:
                self._movement_insertion_order.remove(entity.id)

    def remove_entity_by_id(self, entity_id: str):
        """Remove an entity by its ID."""
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            if entity.thinking:
                self.entity_thinking_count -= 1
            del self.entities[entity_id]
            if entity_id in self._movement_insertion_order:
                self._movement_insertion_order.remove(entity_id)

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
        # 1. Let entities perform their own logic (which may schedule pending moves)
        for entity in self.entities.values():
            entity.tick()
        # Ensure tilemap present
        if self.tilemap is None:
            self.tilemap = Tilemap.from_default()
        # 2. Resolve tilemap entity movements after all have decided
        self._resolve_tile_entity_movements()
        # 3. Perform tile mutation (visual/demo) after movement
        self.tilemap.maybe_mutate()

    # --- Movement & Collision Resolution ---
    def _resolve_tile_entity_movements(self):
        tile_entities: List[TileMapEntity] = [e for e in self.entities.values() if isinstance(e, TileMapEntity)]
        # Stable order: by priority then by insertion order index
        insertion_index = {eid: idx for idx, eid in enumerate(self._movement_insertion_order)}
        tile_entities.sort(key=lambda e: (getattr(e, 'priority', 100), insertion_index.get(e.id, 1_000_000)))

        journal: List[Dict] = []
        # Keep track of updated rectangles for entities that moved successfully this tick
        updated_positions: Dict[str, Location] = {}

        def rect_for(ent: TileMapEntity, loc: Location):
            return (loc.x, loc.y, loc.x + ent.width - 1, loc.y + ent.height - 1)

        def intersects(a, b) -> bool:
            ax1, ay1, ax2, ay2 = a
            bx1, by1, bx2, by2 = b
            return not (ax2 < bx1 or bx2 < ax1 or ay2 < by1 or by2 < ay1)

        for ent in tile_entities:
            from_loc = ent.location
            status = 'no_pending'
            blocked_by = None
            to_loc = ent.location
            attempted = ent.pending_move

            if attempted is not None:
                dx, dy = attempted
                # Enforce constraints
                if dx < -1 or dx > 1 or dy < -1 or dy > 1:
                    status = 'blocked_tile'
                    blocked_by = {"type": "tile", "reason": "invalid_delta"}
                else:
                    target = Location(x=from_loc.x + dx, y=from_loc.y + dy)
                    # Bounds check (top-left and extent within map)
                    if not (0 <= target.x and 0 <= target.y and target.x + ent.width - 1 < self.tilemap.width and target.y + ent.height - 1 < self.tilemap.height):
                        status = 'blocked_tile'
                        blocked_by = {"type": "tile", "reason": "out_of_bounds"}
                    else:
                        # Passability check for every covered tile in target rect
                        impassable = False
                        for y in range(target.y, target.y + ent.height):
                            for x in range(target.x, target.x + ent.width):
                                if not self.tilemap.is_passable(x, y):
                                    impassable = True
                                    blocked_by = {"type": "tile", "reason": "impassable", "tile_type": self.tilemap.tiles[y][x]}
                                    break
                            if impassable:
                                break
                        if impassable:
                            status = 'blocked_tile'
                        else:
                            # Entity collision check against others (use updated positions where available)
                            target_rect = rect_for(ent, target)
                            collision_entity: TileMapEntity | None = None
                            for other in tile_entities:
                                if other.id == ent.id:
                                    continue
                                other_loc = updated_positions.get(other.id, other.location)
                                other_rect = rect_for(other, other_loc)
                                if intersects(target_rect, other_rect):
                                    collision_entity = other
                                    break
                            if collision_entity:
                                status = 'blocked_entity'
                                blocked_by = {"type": "entity", "id": collision_entity.id}
                                # Fire callbacks
                                ent.on_collided(collision_entity, initiated=True)
                                collision_entity.on_collided(ent, initiated=False)
                            else:
                                # Apply move
                                ent.location = target
                                updated_positions[ent.id] = target
                                to_loc = target
                                status = 'moved'
                                ent.on_moved(from_loc, to_loc)
                # Movement processed (success or fail) -> clear pending
                ent.clear_pending_move()
                if status != 'moved' and attempted is not None and status != 'no_pending':
                    ent.on_move_failed(blocked_by['type'] if blocked_by else 'unknown', attempted)

            journal.append({
                'id': ent.id,
                'from': {'x': from_loc.x, 'y': from_loc.y},
                'to': {'x': to_loc.x, 'y': to_loc.y},
                'status': status,
                'blocked_by': blocked_by,
            })

        self.last_movement_journal = journal

    def to_json(self, short: bool = False):
        val = {
            "entities": {eid: entity.to_json(short) for eid, entity in self.entities.items()},
        }
        # Ensure tilemap present
        if not short:
            if self.tilemap is None:
                self.tilemap = Tilemap.from_default()
            if self.tilemap:
                val["tilemap"] = self.tilemap.to_json()

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
            "test": 1015,
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



# Resolve forward references now that World is fully defined.
# This fixes pydantic.errors.PydanticUserError: <Model> is not fully defined when
# instantiating models (e.g., GonkDroid) that inherit from Entity which has a
# forward reference to 'World'.
from simulation.Entity import Entity as _Entity  # Local import to avoid circular issues at module load time.
_Entity.model_rebuild()
from simulation.TileMapEntity import TileMapEntity as _TileMapEntity
try:
    _TileMapEntity.model_rebuild()
except Exception:
    pass
try:
    from simulation.RandomWalker import RandomWalker as _RandomWalker
    _RandomWalker.model_rebuild()
except Exception:
    pass


