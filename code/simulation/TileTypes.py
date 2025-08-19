from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class TileType:
    """Definition of a tile type referenced by integer ID in the tile grid.

    Properties drive both rendering (name, image) and simulation logic (passable, move_speed_scalar).
    The `can_mutate` flag controls whether the random mutation demo logic is allowed to swap tiles
    of this type for another tile type that preserves passability.
    """

    id: int
    name: str
    passable: bool
    move_speed_scalar: float = 1.0
    image: Optional[str] = None
    can_mutate: bool = True
    # Allow future extension without changing schema repeatedly.
    extra: Dict[str, Any] | None = None

    def to_json(self) -> Dict[str, Any]:
        data = asdict(self)
        # Keep compact by dropping None extra
        if data.get("extra") is None:
            data.pop("extra", None)
        return data
