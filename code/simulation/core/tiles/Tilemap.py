from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Iterable
import random
from .TileTypes import TileType


@dataclass
class Tilemap:
    """Simple mock tilemap backing store extracted from World.

    JSON contract (unchanged):
    {
      "width": int,
      "height": int,
      "tiles": List[List[int]],
      "tile_types": Dict[str, Dict],
    }
    """

    width: int = 0
    height: int = 0
    tiles: List[List[int]] = field(default_factory=list)
    # tile type registry (id -> TileType)
    tile_types: Dict[int, TileType] = field(default_factory=dict)

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
        # Register default tile types if registry empty
        if not self.tile_types:
            self._register_default_tile_types()

    # --- Tile type management ---
    def _register_default_tile_types(self):
        self.register_tile_type(TileType(id=0, name="sand", passable=True, move_speed_scalar=1.0, image=None))
        self.register_tile_type(TileType(id=1, name="rock", passable=False, move_speed_scalar=1.0, image=None))
        self.register_tile_type(TileType(id=2, name="pad", passable=True, move_speed_scalar=1.0, image=None))

    def register_tile_type(self, tile_type: TileType):
        if tile_type.id in self.tile_types and self.tile_types[tile_type.id] != tile_type:
            raise ValueError(f"Tile type id {tile_type.id} already registered with different definition")
        self.tile_types[tile_type.id] = tile_type

    def get_tile_type(self, tid: int) -> TileType:
        return self.tile_types[tid]

    def is_passable(self, x: int, y: int) -> bool:
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        tid = self.tiles[y][x]
        tt = self.tile_types.get(tid)
        if tt is None:
            # Unknown type -> treat as impassable for safety
            return False
        return tt.passable

    def to_json(self) -> Dict:
        self.ensure_initialized()
        # IMPORTANT: Keep original contract expected by existing tests / clients.
        # We now also always include 'tile_types' (tests rely on it) while shape test
        # permits its presence.
        return {
            "width": self.width,
            "height": self.height,
            "tiles": self.tiles,
            "tile_types": {tid: tt.to_json() for tid, tt in self.tile_types.items()},
        }

    @classmethod
    def from_default(cls) -> "Tilemap":
        tm = cls()
        tm.ensure_initialized()
        return tm
