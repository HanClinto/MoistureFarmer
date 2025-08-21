from datetime import datetime
from typing import ClassVar, Dict, Optional, List, Type, TYPE_CHECKING
from pydantic import BaseModel

from simulation.GlobalConfig import GlobalConfig
from simulation.LogMessage import LogMessage

if TYPE_CHECKING:
    from simulation.World import World, Simulation

# --- GameObject ---
# A GameObject is an object that is tracked by the simulation.
#  It has a unique identifier, it will receive tick updates, and it can be interacted with.
# For a GameObject to have a location, it must be an Entity.
# For a GameObject to contain components, it must be a Chassis.
# For a GameObject to add modular functionality to an Entity, it must be a Component.
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

    def to_json(self, short: bool = False):
        return {
            "id": self.id,
            "type": self.__class__.__name__,
            # "logs": [log.to_json() for log in self.get_logs()]
        }
    
    def last_message(self) -> Optional[LogMessage]:
        """Return the last log message, or None if there are no logs."""
        if self._log_history and len(self._log_history) > 0:
            return self._log_history[-1]
        return None
