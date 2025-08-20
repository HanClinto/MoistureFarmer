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
      "legend": Dict[str, str],
      "last_mutation": Optional[{"x": int, "y": int, "value": int}]
    }
    """

    width: int = 0
    height: int = 0
    tiles: List[List[int]] = field(default_factory=list)
    # Legacy legend (id->name as strings); kept for backward compatibility with existing clients.
    legend: Dict[str, str] = field(default_factory=lambda: {"0": "sand", "1": "rock", "2": "pad"})
    last_mutation: Optional[Dict[str, int]] = None
    # New: tile type registry (id -> TileType)
    tile_types: Dict[int, TileType] = field(default_factory=dict)
    # Cached mutation candidate ids (only among can_mutate=True and sharing passability with current tile)
    _mutation_candidates_passable: List[int] = field(default_factory=list, repr=False)
    _mutation_candidates_blocked: List[int] = field(default_factory=list, repr=False)

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
        # Register default tile types if registry empty
        if not self.tile_types:
            self._register_default_tile_types()
        self._rebuild_mutation_caches()

    # --- Tile type management ---
    def _register_default_tile_types(self):
        self.register_tile_type(TileType(id=0, name="sand", passable=True, move_speed_scalar=1.0, image=None, can_mutate=True))
        self.register_tile_type(TileType(id=1, name="rock", passable=False, move_speed_scalar=1.0, image=None, can_mutate=False))
        self.register_tile_type(TileType(id=2, name="pad", passable=True, move_speed_scalar=1.0, image=None, can_mutate=True))
        # Keep legend in sync for legacy
        self.legend = {str(tid): tt.name for tid, tt in self.tile_types.items()}

    def register_tile_type(self, tile_type: TileType):
        if tile_type.id in self.tile_types and self.tile_types[tile_type.id] != tile_type:
            raise ValueError(f"Tile type id {tile_type.id} already registered with different definition")
        self.tile_types[tile_type.id] = tile_type
        # Update legend name mapping
        self.legend[str(tile_type.id)] = tile_type.name

    def _rebuild_mutation_caches(self):
        self._mutation_candidates_passable = [tid for tid, tt in self.tile_types.items() if tt.passable and tt.can_mutate]
        # Not used for now (we do not mutate impassables), but retained for completeness.
        self._mutation_candidates_blocked = [tid for tid, tt in self.tile_types.items() if (not tt.passable) and tt.can_mutate]

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

    def maybe_mutate(self):
        """Mutate one random interior tile.

        Mutation now respects tile type passability: we only swap a tile for another tile type
        with the same passability flag, and only among types that have can_mutate=True.
        """
        self.ensure_initialized()
        if self.width <= 2 or self.height <= 2:
            return

        x = random.randint(1, self.width - 2)
        y = random.randint(1, self.height - 2)
        current_tid = self.tiles[y][x]
        current_tt = self.tile_types.get(current_tid)
        if not current_tt:
            return
        candidates: Iterable[int]
        if current_tt.passable:
            candidates = [tid for tid in self._mutation_candidates_passable if tid != current_tid]
        else:
            # Currently we avoid changing passability of impassables; we could allow later.
            candidates = [tid for tid in self._mutation_candidates_blocked if tid != current_tid]
        # If no alternative candidate, skip mutation.
        if not candidates:
            return
        new_tid = random.choice(list(candidates))
        self.tiles[y][x] = new_tid
        self.last_mutation = {"x": x, "y": y, "value": new_tid}

    def to_json(self) -> Dict:
        self.ensure_initialized()
        # IMPORTANT: Keep original contract expected by existing tests / clients.
        # We now also always include 'tile_types' (tests rely on it) while shape test
        # permits its presence.
        return {
            "width": self.width,
            "height": self.height,
            "tiles": self.tiles,
            "legend": self.legend,  # legacy simple mapping
            "last_mutation": self.last_mutation,
            "tile_types": {tid: tt.to_json() for tid, tt in self.tile_types.items()},
        }

    @classmethod
    def from_default(cls) -> "Tilemap":
        tm = cls()
        tm.ensure_initialized()
        return tm
