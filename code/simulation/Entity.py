from typing import ClassVar, Dict, Optional, List, Type, Optional
from pydantic import BaseModel

# --- Entity ---
# Entities are objects that have a location and can move around and interact in the world.
#  In the context of a game simulation, entities will be active sprites on the map
#  They can be droids, players, equipment (such as moisture vaporators), NPCs, enemies, or other interactive elements on the map.

# Entities can contain Components (see Component.py) that provide functionality or attributes, but these components would not be rendered on the map separately.

class Location(BaseModel):
    x: int
    y: int

class GameObject(BaseModel):
    id: Optional[str] = None

    _type_counter: ClassVar[Dict[Type, int]] = {}
    @classmethod
    def generate_id(cls, obj_type: Type) -> str:
        # Generate a unique ID based on the type of the object
        #  Ex: "Motivator_1", "Motivator_2", "PowerPack_1", etc.
        cls._type_counter.setdefault(obj_type, 0)
        cls._type_counter[obj_type] += 1
        return f"{obj_type.__name__}_{cls._type_counter[obj_type]}"

    def __init__(__pydantic_self__, **data):
        super().__init__(**data)
        if not __pydantic_self__.id:
            __pydantic_self__.id = __pydantic_self__.generate_id(__pydantic_self__.__class__)

class Entity(GameObject):
    location: Location = Location(x=0, y=0)  # Default location    
    name: Optional[str] = None
    description: Optional[str] = None

    # Manhattan distance to another entity
    def distance_to(self, other: 'Entity') -> float:
        return abs(self.location.x - other.location.x) + abs(self.location.y - other.location.y)

