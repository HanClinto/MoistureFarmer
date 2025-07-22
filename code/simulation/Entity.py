from datetime import datetime
from typing import ClassVar, Dict, Optional, List, Tuple, Type, TYPE_CHECKING
from pydantic import BaseModel

from simulation.GlobalConfig import GlobalConfig

if TYPE_CHECKING:
    from simulation.World import World, Simulation

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
    
class LogMessage(BaseModel):
    colors: ClassVar[Dict[str, str]] = {
        0: GlobalConfig.INFO_COLOR,
        1: GlobalConfig.WARN_COLOR,
        2: GlobalConfig.ERR_COLOR
    }
    message: str
    level: int            # 0 = info, 1 = warning, 2 = error
    timestamp: datetime   # Internally used for sorting logs within a single tick

    def __str__(self):
        level_str = ["INFO", "WARN", "ERROR"][self.level]
        return f"[{self.timestamp}] [{self.colors[self.level]}{level_str}{GlobalConfig.colors.RESET}] {self.message}"

    def __init__(self, **data):
        super().__init__(**data)
        if not self.timestamp:
            self.timestamp = datetime.now()

    def to_json(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
            "level": self.level,
        }

class GameObject(BaseModel):
    id: Optional[str] = None
    _log_history: List[LogMessage] = []  # List of LogMessage objects

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

    def log(self, message: str, level:int = 0):
        """Log a message with a specific level (0 = info, 1 = warning, 2 = error)"""
        timestamp = datetime.now()
        log_message = LogMessage(message=message, level=level, timestamp=timestamp)
        self._log_history.append(log_message)
        if level >= GlobalConfig.log_print_level:
            print(log_message)

    def info(self, message: str):
        """Log an informational message"""
        self.log(message, level=0)

    def warn(self, message: str):
        """Log a warning message"""
        self.log(message, level=1)

    def error(self, message: str):
        """Log an error message"""
        self.log(message, level=2)

    def get_logs(self) -> List[LogMessage]:
        """Return the log history for this object."""
        return self._log_history

    def to_json(self):
        return {
            "id": self.id,
            "type": self.__class__.__name__,
            # "logs": [log.to_json() for log in self.get_logs()]
        }

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

    def to_json(self):
        return {
            **super().to_json(),
            "name": self.name,
            "description": self.description,
            "location": {"x": self.location.x, "y": self.location.y} if self.location else None,
            # Optionally add more fields here
        }