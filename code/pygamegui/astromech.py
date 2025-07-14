import pygame
import random
import os
from typing import Optional
from entity import Entity
from sprite_sheet import AstromechSpriteSheet

class Astromech(Entity):
    """Astromech droid entity with sprite rendering and AI behavior"""
    
    # Class-level sprite sheet (shared by all astromech instances)
    _sprite_sheet: Optional[AstromechSpriteSheet] = None
    
    def __init__(self, tile_x: int, tile_y: int, tile_size: int = 32):
        super().__init__(tile_x, tile_y, tile_size)
        
        # Load sprite sheet if not already loaded
        if Astromech._sprite_sheet is None:
            sprite_path = os.path.join("..", "resources", "ys_astromech.png")
            try:
                Astromech._sprite_sheet = AstromechSpriteSheet(sprite_path)
            except FileNotFoundError:
                print(f"Warning: Could not load astromech sprite sheet at {sprite_path}")
                Astromech._sprite_sheet = None
        
        # AI behavior timing
        self.think_timer = 0.0
        self.think_interval = random.uniform(1.0, 3.0)  # Think every 1-3 seconds
        
        # Reference to collision manager (set by entity manager)
        self.collision_manager = None
        self.map_width = 0
        self.map_height = 0
    
    def set_world_info(self, collision_manager, map_width: int, map_height: int):
        """Set world information for collision checking"""
        self.collision_manager = collision_manager
        self.map_width = map_width
        self.map_height = map_height
    
    def update_logic(self, dt: float):
        """Astromech-specific update logic"""
        # Only think about moving when not currently moving
        if not self.is_moving:
            self.think_timer += dt
            
            if self.think_timer >= self.think_interval:
                self.think_timer = 0.0
                self.think_interval = random.uniform(1.0, 3.0)  # Reset think interval
                self.decide_movement()
    
    def decide_movement(self):
        """Decide where to move next"""
        # Get possible adjacent tiles
        adjacent_tiles = [
            (self.tile_x, self.tile_y - 1),  # Up
            (self.tile_x + 1, self.tile_y),  # Right
            (self.tile_x, self.tile_y + 1),  # Down
            (self.tile_x - 1, self.tile_y),  # Left
        ]
        
        # Filter valid tiles
        valid_tiles = []
        for tx, ty in adjacent_tiles:
            if self.is_tile_valid(tx, ty):
                valid_tiles.append((tx, ty))
        
        # Sometimes don't move (add current position as option)
        if random.random() < 0.3:  # 30% chance to stay put
            valid_tiles.append((self.tile_x, self.tile_y))
        
        # Choose a random valid tile
        if valid_tiles:
            target_x, target_y = random.choice(valid_tiles)
            if target_x != self.tile_x or target_y != self.tile_y:
                self.start_move_to_tile(target_x, target_y)
    
    def is_tile_valid(self, tile_x: int, tile_y: int) -> bool:
        """Check if a tile is valid for movement"""
        # Check map bounds
        if tile_x < 0 or tile_y < 0 or tile_x >= self.map_width or tile_y >= self.map_height:
            return False
        
        # Check collision if collision manager is available
        if self.collision_manager:
            return not self.collision_manager.is_tile_blocking(tile_x, tile_y)
        
        return True
    
    def render(self, screen: pygame.Surface, camera, zoom: float):
        """Render the astromech droid"""
        if Astromech._sprite_sheet is None:
            # Fallback: render as a colored circle
            world_x, world_y = self.get_render_position()
            screen_x, screen_y = camera.world_to_screen(world_x, world_y)
            radius = int(12 * zoom)
            pygame.draw.circle(screen, (100, 150, 255), (screen_x, screen_y), radius)
            return
        
        # Get the appropriate sprite for current direction
        sprite = Astromech._sprite_sheet.get_scaled_sprite(self.direction, zoom)
        
        # Calculate render position
        world_x, world_y = self.get_render_position()
        screen_x, screen_y = camera.world_to_screen(world_x, world_y)
        
        # Center the sprite on the position
        sprite_rect = sprite.get_rect()
        sprite_rect.center = (screen_x, screen_y)
        
        # Render the sprite
        screen.blit(sprite, sprite_rect)
    
    def __str__(self):
        """String representation for debugging"""
        return f"Astromech(tile={self.tile_x},{self.tile_y}, world={self.world_x:.1f},{self.world_y:.1f}, dir={self.direction}, moving={self.is_moving})"
