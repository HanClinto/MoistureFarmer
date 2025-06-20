import pygame
import math
from typing import Tuple, Optional
from abc import ABC, abstractmethod

class Entity(ABC):
    """Base class for all entities in the simulation"""
    
    def __init__(self, tile_x: int, tile_y: int, tile_size: int = 32):
        # Tile-based position (logical position)
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.tile_size = tile_size
        
        # World position (pixel position for rendering)
        self.world_x = float(tile_x * tile_size + tile_size // 2)  # Center of tile
        self.world_y = float(tile_y * tile_size + tile_size // 2)
        
        # Movement state
        self.is_moving = False
        self.move_start_x = self.world_x
        self.move_start_y = self.world_y
        self.move_target_x = self.world_x
        self.move_target_y = self.world_y
        self.move_progress = 0.0
        self.move_duration = 2.0  # seconds to move one tile
        
        # Direction (0=down, 1=right, 2=left, 3=up)
        self.direction = 0
    
    def start_move_to_tile(self, target_tile_x: int, target_tile_y: int):
        """Start moving to a target tile"""
        if self.is_moving:
            return  # Already moving
        
        # Calculate target world position (center of target tile)
        target_world_x = target_tile_x * self.tile_size + self.tile_size // 2
        target_world_y = target_tile_y * self.tile_size + self.tile_size // 2
        
        # Set up movement
        self.move_start_x = self.world_x
        self.move_start_y = self.world_y
        self.move_target_x = target_world_x
        self.move_target_y = target_world_y
        self.move_progress = 0.0
        self.is_moving = True
        
        # Update direction based on movement
        dx = target_tile_x - self.tile_x
        dy = target_tile_y - self.tile_y
        self.update_direction(dx, dy)
        
        # Update logical position
        self.tile_x = target_tile_x
        self.tile_y = target_tile_y
    
    def update_direction(self, dx: int, dy: int):
        """Update direction based on movement delta"""
        if dx > 0:
            self.direction = 1  # Right
        elif dx < 0:
            self.direction = 2  # Left
        elif dy > 0:
            self.direction = 0  # Down
        elif dy < 0:
            self.direction = 3  # Up
    
    def update(self, dt: float):
        """Update entity state"""
        if self.is_moving:
            self.move_progress += dt / self.move_duration
            
            if self.move_progress >= 1.0:
                # Movement complete
                self.move_progress = 1.0
                self.is_moving = False
                self.world_x = self.move_target_x
                self.world_y = self.move_target_y
            else:
                # Interpolate position using easing function
                t = self.ease_in_out(self.move_progress)
                self.world_x = self.lerp(self.move_start_x, self.move_target_x, t)
                self.world_y = self.lerp(self.move_start_y, self.move_target_y, t)
        
        self.update_logic(dt)
    
    def ease_in_out(self, t: float) -> float:
        """Smooth easing function for movement"""
        return t * t * (3.0 - 2.0 * t)
    
    def lerp(self, start: float, end: float, t: float) -> float:
        """Linear interpolation"""
        return start + (end - start) * t
    
    def get_render_position(self) -> Tuple[float, float]:
        """Get the current render position in world coordinates"""
        return self.world_x, self.world_y
    
    @abstractmethod
    def update_logic(self, dt: float):
        """Override this for entity-specific logic"""
        pass
    
    @abstractmethod
    def render(self, screen: pygame.Surface, camera, zoom: float):
        """Override this for entity-specific rendering"""
        pass
