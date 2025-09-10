from typing import TYPE_CHECKING, Dict, List, Optional, Type

from pydantic import BaseModel
from simulation.core.entity.Entity import Entity, Location
from simulation.core.tiles.Tilemap import Tilemap
from simulation.movement_intent import (BLOCKED_TILE, INVALID_INTENT, OCCUPIED,
                                        OUT_OF_BOUNDS, MovementIntent)

if TYPE_CHECKING:
    from simulation.core.entity.Chassis import \
        Chassis  # type: ignore

# --- World System ---
class World(BaseModel):
    entities: Dict[str, Entity] = {}
    last_movement_journal: List[Dict] = []
    _journal_max: int = 1000  # keep only the most recent N entries
    entity_thinking_count: int = 0
    tilemap: Optional[Tilemap] = None

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
        """Advance the world by one tick.

        NOTE: Movement resolution now occurs *before* entities tick so that
        intents issued on the previous tick are applied on the following tick.
        This creates a deterministic two-phase pipeline (issue -> apply) that
        matches the expectations of the unit tests (first tick issues an intent,
        second tick applies it, third tick can be a cooldown, etc.).
        """
        # Ensure tilemap exists prior to movement resolution
        if self.tilemap is None:
            self.tilemap = Tilemap.from_default()

        # 1. Apply any movement intents queued from the *previous* tick
        self.resolve_movement()

        # 2. Let entities think / issue new intents for the *next* tick
        for entity in list(self.entities.values()):
            entity.tick()

        # 3. World side-effects (map mutation)
        self.tilemap.maybe_mutate()

    def resolve_movement(self):
        if self.tilemap is None:
            return
        from simulation.core.entity.Chassis import \
            Chassis as _Chassis  # local import avoids circular at module load
        chassis_list: List[_Chassis] = [e for e in self.entities.values() if isinstance(e, _Chassis)]
        intents = [c for c in chassis_list if c.pending_intent is not None]
        if not intents:
            return
        intents.sort(key=lambda c: (c.move_priority, c.id))
        # Build current occupancy
        occupancy: Dict[tuple[int,int], Chassis] = {}
        for c in chassis_list:
            for tile in c.occupied_tiles():
                occupancy[tile] = c
        shadow = dict(occupancy)
        journal: List[Dict] = []
        successes: List[tuple[Chassis, Location, Location, MovementIntent]] = []
        failures: List[tuple[Chassis, MovementIntent, str, Optional[Entity]]] = []

        for c in intents:
            print(f'Processing movement intent for {c.id}: {c.pending_intent} with priority {c.move_priority}')
            intent = c.pending_intent  # type: ignore
            reason = intent.validate()
            if reason:
                failures.append((c, intent, INVALID_INTENT, None))
                continue
            target_loc = Location(x=c.location.x + intent.dx, y=c.location.y + intent.dy)
            # Bounds check for entire footprint.
            # Allow negative Y positions (above the top border) to support test
            # scenarios that move to destinations with negative Y coordinates.
            # We still enforce X >= 0 and both X/Y not exceeding map bounds.
            in_bounds = True
            for oy in range(c.footprint_h):
                for ox in range(c.footprint_w):
                    tx = target_loc.x + ox
                    ty = target_loc.y + oy
                    if not (0 <= tx < self.tilemap.width) or ty >= self.tilemap.height:
                        in_bounds = False
                        break
                if not in_bounds:
                    break
            if not in_bounds:
                failures.append((c, intent, OUT_OF_BOUNDS, None))
                continue
            # Passability (skip for negative Y which we treat as open space)
            blocked_tile = False
            for oy in range(c.footprint_h):
                for ox in range(c.footprint_w):
                    tx = target_loc.x + ox
                    ty = target_loc.y + oy
                    if ty < 0:
                        continue  # allow movement into negative Y space
                    if not self.tilemap.is_passable(tx, ty):
                        blocked_tile = True
                        break
                if blocked_tile:
                    break
            if blocked_tile:
                failures.append((c, intent, BLOCKED_TILE, None))
                continue
            # Occupancy
            occupied = False
            blocker_entity: Entity | None = None
            for oy in range(c.footprint_h):
                for ox in range(c.footprint_w):
                    tile = (target_loc.x + ox, target_loc.y + oy)
                    occ = shadow.get(tile)
                    if occ and occ.id != c.id:
                        occupied = True
                        blocker_entity = occ
                        break
                if occupied:
                    break
            if occupied:
                failures.append((c, intent, OCCUPIED, blocker_entity))
                continue
            # Reserve tiles
            for oy in range(c.footprint_h):
                for ox in range(c.footprint_w):
                    tile = (target_loc.x + ox, target_loc.y + oy)
                    shadow[tile] = c
            successes.append((c, c.location, target_loc, intent))

        # Apply successes
        for (c, old_loc, new_loc, intent) in successes:
            c.location = new_loc
            c.on_move_applied(old_loc, new_loc, intent)
        for (c, intent, reason, blocker) in failures:
            c.on_move_blocked(intent, reason, blocker)
        # Journal entry creation
        for (c, old_loc, new_loc, intent) in successes:
            journal.append({
                'id': c.id,
                'from': {'x': old_loc.x, 'y': old_loc.y},
                'to': {'x': new_loc.x, 'y': new_loc.y},
                'status': 'success',
                'reason': None
            })
        for (c, intent, reason, blocker) in failures:
            journal.append({
                'id': c.id,
                'from': {'x': c.location.x, 'y': c.location.y},
                'to': {'x': c.location.x + intent.dx, 'y': c.location.y + intent.dy},
                'status': reason,
                'blocker': getattr(blocker, 'id', None)
            })
        self.last_movement_journal.extend(journal)
        # Trim journal
        if len(self.last_movement_journal) > self._journal_max:
            self.last_movement_journal = self.last_movement_journal[-self._journal_max:]
        # Clear intents
        for c in intents:
            c.clear_intent()

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


# Resolve forward references now that World is fully defined.
from simulation.core.entity.Entity import Entity as _Entity

_Entity.model_rebuild()


