from typing import Dict, Optional
from pydantic import BaseModel

from simulation.Entity import Entity

# --- World System ---
class World(BaseModel):
    entities: Dict[str, Entity] = {}

    def __init__(self, **data):
        super().__init__(**data)

    def add_entity(self, entity: Entity):
        self.entities[entity.id] = entity

    def get_entity(self, obj_id: str) -> Optional[Entity]:
        if obj_id in self.entities:
            return self.entities[obj_id]
        else:
            # TODO: Raise this as an error that can be seen by any AI
            print(f"Entity with ID {obj_id} not found in the world.")
            return None

    def tick(self):
        for entity in self.entities.values():
            entity.tick(self)

