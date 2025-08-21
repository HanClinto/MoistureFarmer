from typing import TYPE_CHECKING, Optional

from simulation.entity.GameObject import GameObject
from simulation.Location import Location

if TYPE_CHECKING:
    from simulation.World import World

# --- Entity ---
# Entities are objects that have a location and can move around and interact in the world.
#  In the context of a game simulation, entities will be active sprites on the map
#  They can be droids, players, equipment (such as moisture vaporators), NPCs, enemies, or other interactive elements on the map.
class Entity(GameObject):
    location: Location = Location(x=0, y=0)  # Default location
    name: Optional[str] = None
    description: Optional[str] = None
    world: Optional['World'] = None  # Reference to the world this entity belongs to
    model: str = "Generic Entity"  # Default model name

    # Manhattan distance to another entity
    def distance_to(self, other: 'Entity') -> float:
        return abs(self.location.x - other.location.x) + abs(self.location.y - other.location.y)

    def tick(self):
        # This method is called every tick in the simulation.
        # Entities can override this method to implement their own behavior.
        self.info(f"Entity {self.id} at {self.location} ticked.")

    def to_json(self, short: bool = False):
        val = {
            **super().to_json(short),
            "location": {"x": self.location.x, "y": self.location.y},
        }
        if self.name:
            val["name"] = self.name
            
        if not short:
            if self.description:
                val["description"] = self.description
            if self.model:
                val["model"] = self.model

        return val
