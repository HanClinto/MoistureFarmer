from __future__ import annotations

import random
from typing import ClassVar, Dict

from .component.Chassis import Chassis, ComponentSlot

class RandomWalker(Chassis):
    """Simple autonomous chassis that attempts a random 8-way step each think interval.

    Legacy behavior ported from TileMapEntity version; uses Chassis.request_move.
    Footprint defaults to 1x1; enlarge via footprint_w/footprint_h if needed.
    """

    think_interval: int = 1  # ticks between movement attempts
    _cooldown: int = 0
    footprint_w: int = 1
    footprint_h: int = 1

    # No components by default; declare as ClassVar so Pydantic doesn't treat it as a model field override
    slots: ClassVar[Dict[str, ComponentSlot]] = {}

    def tick(self):  # Called every world tick
        # First tick components (none by default)
        super().tick()
        if self._cooldown > 0:
            self._cooldown -= 1
            return
        self._cooldown = self.think_interval
        world = self.world
        if not world or not getattr(world, 'tilemap', None):
            return
        tm = world.tilemap
        # Try a handful of random directions
        for _ in range(8):
            dx = random.randint(-1, 1)
            dy = random.randint(-1, 1)
            if dx == 0 and dy == 0:
                continue
            # Validate target footprint
            target_x = self.location.x + dx
            target_y = self.location.y + dy
            if not (0 <= target_x < tm.width and 0 <= target_y < tm.height):
                continue
            passable = True
            for oy in range(self.footprint_h):
                for ox in range(self.footprint_w):
                    tx = target_x + ox
                    ty = target_y + oy
                    if not (0 <= tx < tm.width and 0 <= ty < tm.height) or not tm.is_passable(tx, ty):
                        passable = False
                        break
                if not passable:
                    break
            if not passable:
                continue
            if self.request_move(dx, dy):
                break

