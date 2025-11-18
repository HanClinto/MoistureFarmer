from typing import TYPE_CHECKING, Dict, List, Optional, Type

from pydantic import BaseModel
from simulation.core.entity.Entity import Entity, Location
from simulation.core.tiles.Tilemap import Tilemap

if TYPE_CHECKING:
    from simulation.core.entity.Chassis import \
        Chassis  # type: ignore

# --- World System ---
class World(BaseModel):
    entities: Dict[str, Entity] = {}
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
        """
        # Ensure tilemap exists prior to movement resolution
        if self.tilemap is None:
            self.tilemap = Tilemap.from_default()

        # 1. Let entities perform their own logic (which may schedule pending moves)
        for entity in list(self.entities.values()):
            entity.tick()

    def is_passable(self, entity: Entity, x: int, y: int) -> bool:
        # Check every entity in the world for collision
        entity_bounds = entity.bounds

        for other_entity in list(self.entities.values()):
            if other_entity.id == entity.id:
                continue  # Skip self
            other_bounds = other_entity.bounds
            if (other_bounds.intersects(entity_bounds)):
                return False  # Collision detected

        # Check tilemap passability
        if self.tilemap:
            for ox in range(entity_bounds.width):
                for oy in range(entity_bounds.height):
                    tx = x + ox
                    ty = y + oy
                    if not self.tilemap.is_passable(tx, ty):
                        return False

        return True

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


