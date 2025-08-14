from __future__ import annotations

from typing import Optional, Tuple, Iterable
from pydantic import BaseModel

from .Entity import Entity, Location

class TileMapEntity(Entity):
    """Entity that occupies an axis-aligned rectangle in the tilemap (top-left anchored).

    Movement is requested by setting a pending (dx, dy) translation (each -1..1) which will
    be resolved centrally by the World after all entities tick() each simulation step.
    """

    width: int = 1
    height: int = 1
    # movement priority: lower processed earlier (ties by insertion order controlled by World)
    priority: int = 100
    # Pending move delta (dx, dy) for next resolution pass
    pending_move: Optional[Tuple[int, int]] = None

    def set_pending_move(self, dx: int, dy: int):
        if dx < -1 or dx > 1 or dy < -1 or dy > 1:
            raise ValueError("TileMapEntity pending move deltas must be in range -1..1")
        self.pending_move = (dx, dy)

    def clear_pending_move(self):
        self.pending_move = None

    def occupied_tiles(self, at_location: Location | None = None) -> Iterable[tuple[int, int]]:
        loc = at_location or self.location
        for oy in range(self.height):
            for ox in range(self.width):
                yield (loc.x + ox, loc.y + oy)

    # --- Callbacks (default no-op) ---
    def on_collided(self, other: 'TileMapEntity', initiated: bool):
        pass

    def on_move_failed(self, reason: str, attempted: tuple[int, int]):
        pass

    def on_moved(self, from_loc: Location, to_loc: Location):
        pass
