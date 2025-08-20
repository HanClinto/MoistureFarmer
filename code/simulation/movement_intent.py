from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

# Failure reason constants
OUT_OF_BOUNDS = "out_of_bounds"
BLOCKED_TILE = "blocked_tile"
OCCUPIED = "occupied"
INVALID_INTENT = "invalid_intent"
NO_POWER = "no_power"
COOLDOWN = "cooldown"

@dataclass(frozen=True)
class MovementIntent:
    """Immutable intent for movement for the current tick.

    kind: "step" is the only supported movement today. Future kinds could include
    "teleport" or "push".
    """
    dx: int
    dy: int
    kind: str = "step"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_noop(self) -> bool:
        return self.dx == 0 and self.dy == 0

    def validate(self) -> Optional[str]:
        """Return None if valid, else failure reason string (INVALID_INTENT)."""
        if self.kind == "step":
            if abs(self.dx) > 1 or abs(self.dy) > 1:
                return INVALID_INTENT
            if self.dx == 0 and self.dy == 0:
                return INVALID_INTENT
        else:
            # Unknown kinds not yet implemented
            return INVALID_INTENT
        return None

__all__ = [
    "MovementIntent",
    "OUT_OF_BOUNDS",
    "BLOCKED_TILE",
    "OCCUPIED",
    "INVALID_INTENT",
    "NO_POWER",
    "COOLDOWN",
]
