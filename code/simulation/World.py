from typing import Dict, List, Optional, Type
from pydantic import BaseModel

from simulation.Entity import Entity

# --- World System ---
class World(BaseModel):
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
        for entity in self.entities.values():
            entity.tick(self)

