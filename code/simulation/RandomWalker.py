from __future__ import annotations

import random
from typing import Optional

from .TileMapEntity import TileMapEntity
from .Entity import Location

class RandomWalker(TileMapEntity):
    """A simple autonomous tilemap entity that attempts a random 8-way step each think interval.

    It validates the target fits within bounds and only traverses passable tiles.
    If no valid move is found after a few attempts, it stays put for that tick.
    """

    think_interval: int = 1  # ticks between movement attempts
    _cooldown: int = 0

    def tick(self):  # Called every world tick
        # Defer to base for any shared logic (currently none)
        if self._cooldown > 0:
            self._cooldown -= 1
            return
        self._cooldown = self.think_interval
        world = self.world
        if not world or not world.tilemap:
            return
        tm = world.tilemap
        # Try a handful of random directions
        for _ in range(8):
            dx = random.randint(-1, 1)
            dy = random.randint(-1, 1)
            if dx == 0 and dy == 0:
                continue
            target = Location(x=self.location.x + dx, y=self.location.y + dy)
            # Bounds (entity may be >1x1 in future)
            if not (0 <= target.x < tm.width and 0 <= target.y < tm.height):
                continue
            # Passability check for occupied footprint
            passable = True
            for oy in range(self.height):
                for ox in range(self.width):
                    tx = target.x + ox
                    ty = target.y + oy
                    if not (0 <= tx < tm.width and 0 <= ty < tm.height) or not tm.is_passable(tx, ty):
                        passable = False
                        break
                if not passable:
                    break
            if not passable:
                continue
            try:
                self.set_pending_move(dx, dy)
            except Exception:
                # Invalid delta (shouldn't happen with -1..1) just skip
                continue
            break

# Ensure pydantic resolves any forward refs after World definition imported elsewhere
try:
    RandomWalker.model_rebuild()
except Exception:
    pass
