import pygame
import os
from typing import List, Tuple

class SpriteSheet:
    """Utility class for handling sprite sheets"""
    
    def __init__(self, image_path: str):
        """Load a sprite sheet from file"""
        self.image_path = image_path
        self.sprite_sheet = None
        self.load_image()
    
    def load_image(self):
        """Load the sprite sheet image"""
        if not os.path.exists(self.image_path):
            raise FileNotFoundError(f"Sprite sheet not found: {self.image_path}")
        
        self.sprite_sheet = pygame.image.load(self.image_path).convert_alpha()
        print(f"Loaded sprite sheet: {self.image_path} ({self.sprite_sheet.get_width()}x{self.sprite_sheet.get_height()})")
    
    def get_sprite(self, x: int, y: int, width: int, height: int) -> pygame.Surface:
        """Extract a single sprite from the sheet"""
        if not self.sprite_sheet:
            raise ValueError("Sprite sheet not loaded")
        
        rect = pygame.Rect(x, y, width, height)
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(self.sprite_sheet, (0, 0), rect)
        return sprite
    
    def get_sprites_column(self, x: int, width: int, height: int, count: int) -> List[pygame.Surface]:
        """Extract a vertical column of sprites"""
        sprites = []
        for i in range(count):
            y = i * height
            sprite = self.get_sprite(x, y, width, height)
            sprites.append(sprite)
        return sprites


class AstromechSpriteSheet(SpriteSheet):
    """Specific sprite sheet handler for astromech droids"""
    
    SPRITE_SIZE = 32
    DIRECTION_DOWN = 0
    DIRECTION_RIGHT = 1
    DIRECTION_LEFT = 2
    DIRECTION_UP = 3
    
    def __init__(self, image_path: str):
        super().__init__(image_path)
        self.directional_sprites = self.load_directional_sprites()
    
    def load_directional_sprites(self) -> List[pygame.Surface]:
        """Load the 4 directional sprites (down, right, left, up)"""
        return self.get_sprites_column(0, self.SPRITE_SIZE, self.SPRITE_SIZE, 4)
    
    def get_sprite_for_direction(self, direction: int) -> pygame.Surface:
        """Get the sprite for a specific direction"""
        if 0 <= direction < len(self.directional_sprites):
            return self.directional_sprites[direction]
        return self.directional_sprites[self.DIRECTION_DOWN]  # Default to down
    
    def get_scaled_sprite(self, direction: int, scale: float) -> pygame.Surface:
        """Get a scaled sprite for a specific direction"""
        sprite = self.get_sprite_for_direction(direction)
        if scale != 1.0:
            new_size = (int(self.SPRITE_SIZE * scale), int(self.SPRITE_SIZE * scale))
            return pygame.transform.scale(sprite, new_size)
        return sprite
