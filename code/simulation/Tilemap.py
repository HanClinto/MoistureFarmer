from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import random


@dataclass
class Tilemap:
    """Simple mock tilemap backing store extracted from World.

    JSON contract (unchanged):
    {
      "width": int,
      "height": int,
      "tiles": List[List[int]],
      "legend": Dict[str, str],
      "last_mutation": Optional[{"x": int, "y": int, "value": int}]
    }
    """

    width: int = 0
    height: int = 0
    tiles: List[List[int]] = field(default_factory=list)
    legend: Dict[str, str] = field(default_factory=lambda: {"0": "sand", "1": "rock", "2": "pad"})
    last_mutation: Optional[Dict[str, int]] = None

    def ensure_initialized(self):
        """Lazily create the default map if not yet initialized.
        Default: 128x128, border=1 (rock), interior=0 (sand), center=2 (pad).
        """
        if self.tiles:
            return

        width, height = 128, 128
        tiles: List[List[int]] = []
        for y in range(height):
            row: List[int] = []
            for x in range(width):
                if x == 0 or y == 0 or x == width - 1 or y == height - 1:
                    row.append(1)
                else:
                    row.append(0)
            tiles.append(row)

        center_x, center_y = width // 2, height // 2
        tiles[center_y][center_x] = 2

        self.width = width
        self.height = height
        self.tiles = tiles
        self.last_mutation = None

    def maybe_mutate(self):
        """Mutate one random interior tile with bias to sand; update last_mutation."""
        self.ensure_initialized()
        if self.width <= 2 or self.height <= 2:
            return

        x = random.randint(1, self.width - 2)
        y = random.randint(1, self.height - 2)
        new_val = random.choice([0, 0, 0, 1, 2])
        self.tiles[y][x] = new_val
        self.last_mutation = {"x": x, "y": y, "value": new_val}

    def to_json(self) -> Dict:
        self.ensure_initialized()
        return {
            "width": self.width,
            "height": self.height,
            "tiles": self.tiles,
            "legend": self.legend,
            "last_mutation": self.last_mutation,
        }

    @classmethod
    def from_default(cls) -> "Tilemap":
        tm = cls()
        tm.ensure_initialized()
        return tm
