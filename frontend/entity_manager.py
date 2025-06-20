import pygame
import random
from typing import List
from entity import Entity
from astromech import Astromech

class EntityManager:
    """Manages all entities in the simulation"""
    
    def __init__(self, map_width: int, map_height: int, tile_size: int = 32):
        self.entities: List[Entity] = []
        self.map_width = map_width
        self.map_height = map_height
        self.tile_size = tile_size
        self.collision_manager = None
    
    def set_collision_manager(self, collision_manager):
        """Set the collision manager for entity movement validation"""
        self.collision_manager = collision_manager
        
        # Update all existing entities with world info
        for entity in self.entities:
            if isinstance(entity, Astromech):
                entity.set_world_info(collision_manager, self.map_width, self.map_height)
    
    def spawn_astromech(self, tile_x: int, tile_y: int) -> Astromech:
        """Spawn an astromech droid at the specified tile position"""
        astromech = Astromech(tile_x, tile_y, self.tile_size)
        
        # Set world info if collision manager is available
        if self.collision_manager:
            astromech.set_world_info(self.collision_manager, self.map_width, self.map_height)
        
        self.entities.append(astromech)
        print(f"Spawned astromech at tile ({tile_x}, {tile_y})")
        return astromech
    def spawn_random_astromechs(self, count: int, max_attempts: int = 100, spawn_center_x: int = None, spawn_center_y: int = None, spawn_radius: int = None):
        """Spawn multiple astromech droids at random valid locations
        
        Args:
            count: Number of astromechs to spawn
            max_attempts: Maximum attempts to find valid spawn locations
            spawn_center_x: Center X tile for constrained spawning (optional)
            spawn_center_y: Center Y tile for constrained spawning (optional)
            spawn_radius: Maximum distance from center in tiles (optional)
        """
        spawned = 0
        attempts = 0
        
        while spawned < count and attempts < max_attempts:
            # Generate random tile position
            if spawn_center_x is not None and spawn_center_y is not None and spawn_radius is not None:
                # Constrained spawning within radius
                tile_x, tile_y = self._generate_random_position_in_radius(
                    spawn_center_x, spawn_center_y, spawn_radius
                )
            else:
                # Random spawning anywhere on map
                tile_x = random.randint(0, self.map_width - 1)
                tile_y = random.randint(0, self.map_height - 1)
            
            # Check if tile is valid for spawning
            if self.is_spawn_location_valid(tile_x, tile_y):
                self.spawn_astromech(tile_x, tile_y)
                spawned += 1
            
            attempts += 1
        
        if spawned < count:
            print(f"Warning: Could only spawn {spawned}/{count} astromechs after {attempts} attempts")
        else:
            print(f"Successfully spawned {spawned} astromechs")
        
    def _generate_random_position_in_radius(self, center_x: int, center_y: int, radius: int) -> tuple:
        """Generate a random position within a circular radius of the center"""
        import math
        
        # Generate random angle and distance for uniform distribution in circle
        angle = random.uniform(0, 2 * math.pi)  # Random angle in radians
        # Use square root for uniform distribution within circle
        distance = radius * math.sqrt(random.uniform(0, 1))
        
        # Convert to tile coordinates
        offset_x = int(distance * math.cos(angle))
        offset_y = int(distance * math.sin(angle))
        
        # Calculate final position, ensuring we stay within map bounds
        tile_x = max(0, min(self.map_width - 1, center_x + offset_x))
        tile_y = max(0, min(self.map_height - 1, center_y + offset_y))
        
        return tile_x, tile_y
    
    def is_spawn_location_valid(self, tile_x: int, tile_y: int) -> bool:
        """Check if a tile is valid for spawning entities"""
        # Check bounds
        if tile_x < 0 or tile_y < 0 or tile_x >= self.map_width or tile_y >= self.map_height:
            return False
        
        # Check collision if collision manager is available
        if self.collision_manager and self.collision_manager.is_tile_blocking(tile_x, tile_y):
            return False
        
        # Check if any entity is already at this location
        for entity in self.entities:
            if entity.tile_x == tile_x and entity.tile_y == tile_y:
                return False
        
        return True
    
    def update(self, dt: float):
        """Update all entities"""
        for entity in self.entities:
            entity.update(dt)
    
    def render(self, screen: pygame.Surface, camera, zoom: float):
        """Render all entities"""
        for entity in self.entities:
            entity.render(screen, camera, zoom)
    
    def get_entity_count(self) -> int:
        """Get the total number of entities"""
        return len(self.entities)
    
    def get_astromech_count(self) -> int:
        """Get the number of astromech droids"""
        return sum(1 for entity in self.entities if isinstance(entity, Astromech))
    
    def clear_entities(self):
        """Remove all entities"""
        self.entities.clear()
        print("Cleared all entities")
    
    def remove_entity(self, entity: Entity):
        """Remove a specific entity"""
        if entity in self.entities:
            self.entities.remove(entity)
    
    def get_entities_at_tile(self, tile_x: int, tile_y: int) -> List[Entity]:
        """Get all entities at a specific tile position"""
        return [entity for entity in self.entities if entity.tile_x == tile_x and entity.tile_y == tile_y]
