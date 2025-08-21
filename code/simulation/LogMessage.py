from datetime import datetime
from typing import ClassVar, Dict

from pydantic import BaseModel
from simulation.GlobalConfig import GlobalConfig


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