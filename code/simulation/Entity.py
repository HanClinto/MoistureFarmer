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

    def distance_to(self, other: 'Location') -> float:
        # Calculate the Manhattan distance to another location
        return abs(self.x - other.x) + abs(self.y - other.y)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Location):
            return NotImplemented
        return self.x == other.x and self.y == other.y
    
    def __add__(self, other: 'Location') -> 'Location':
        if not isinstance(other, Location):
            return NotImplemented
        return Location(x=self.x + other.x, y=self.y + other.y)
    
    def __sub__(self, other: 'Location') -> 'Location':
        if not isinstance(other, Location):
            return NotImplemented
        return Location(x=self.x - other.x, y=self.y - other.y)
    
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

    def __init__(self, **data):
        super().__init__(**data)
        if not self.id:
            self.id = self.generate_id(self.__class__)

class Entity(GameObject):
    location: Location = Location(x=0, y=0)  # Default location
    name: Optional[str] = None
    description: Optional[str] = None
    world: Optional['World'] = None  # Reference to the world this entity belongs to

    # Manhattan distance to another entity
    def distance_to(self, other: 'Entity') -> float:
        return abs(self.location.x - other.location.x) + abs(self.location.y - other.location.y)

    def tick(self):
        # This method is called every tick in the simulation.
        # Entities can override this method to implement their own behavior.
        print(f"Entity {self.id} at {self.location} ticked.")