import pygame
from typing import Tuple, Optional

class Camera:
    """Camera system for smooth panning and zooming around the map"""
    def __init__(self, screen_width: int, screen_height: int):
        self.x = 0.0
        self.y = 0.0
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.speed = 300  # pixels per second

        # Zoom levels as powers of 2 for pixel-perfect scaling
        self.zoom_levels = [0.5, 1.0, 2.0, 4.0]
        self.current_zoom_index = 3  # Start at 1.0x (index 3)
        self.zoom = self.zoom_levels[self.current_zoom_index]

    def update(self, dt: float, keys_pressed, mouse_pos: Optional[Tuple[int, int]] = None):
        """Update camera position based on input"""
        movement_x = 0
        movement_y = 0

        # Keyboard controls
        if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
            movement_x -= self.speed * dt
        if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
            movement_x += self.speed * dt
        if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
            movement_y -= self.speed * dt
        if keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
            movement_y += self.speed * dt

        # Apply movement
        self.x += movement_x
        self.y += movement_y

    def get_visible_tiles(self, tile_width: int, tile_height: int, map_width: int, map_height: int):
        """Calculate which tiles are visible on screen"""
        # Add padding to ensure smooth scrolling
        padding = 2

        # Account for zoom when calculating visible area
        scaled_tile_width = tile_width * self.zoom
        scaled_tile_height = tile_height * self.zoom

        start_x = max(0, int(self.x // scaled_tile_width) - padding)
        start_y = max(0, int(self.y // scaled_tile_height) - padding)
        end_x = min(map_width, int((self.x + self.screen_width) // scaled_tile_width) + padding + 1)
        end_y = min(map_height, int((self.y + self.screen_height) // scaled_tile_height) + padding + 1)

        return start_x, start_y, end_x, end_y

    def zoom_at_point(self, zoom_direction: int, mouse_x: int, mouse_y: int):
        """Zoom at a specific point (usually mouse position) using discrete zoom levels"""
        old_zoom = self.zoom
        old_zoom_index = self.current_zoom_index

        # Calculate new zoom index
        new_zoom_index = self.current_zoom_index + zoom_direction
        new_zoom_index = max(0, min(len(self.zoom_levels) - 1, new_zoom_index))

        if new_zoom_index != old_zoom_index:
            self.current_zoom_index = new_zoom_index
            new_zoom = self.zoom_levels[self.current_zoom_index]

            # Calculate the world coordinate that the mouse is pointing to before zoom
            world_x_before = (self.x + mouse_x) / old_zoom
            world_y_before = (self.y + mouse_y) / old_zoom

            # Update zoom
            self.zoom = new_zoom

            # Calculate what the camera position should be to keep the same world point under the mouse
            self.x = world_x_before * self.zoom - mouse_x
            self.y = world_y_before * self.zoom - mouse_y

    def clamp_to_tilemap(self, map_width: int, map_height: int, tile_width: int, tile_height: int):
        """Ensure the camera stays within the bounds of the tilemap"""
        map_pixel_width = map_width * tile_width * self.zoom
        map_pixel_height = map_height * tile_height * self.zoom

        self.x = max(0, min(self.x, map_pixel_width - self.screen_width))
        self.y = max(0, min(self.y, map_pixel_height - self.screen_height))

    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates"""
        screen_x = int(world_x * self.zoom - self.x)
        screen_y = int(world_y * self.zoom - self.y)
        return screen_x, screen_y

    def screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates"""
        world_x = (screen_x + self.x) / self.zoom
        world_y = (screen_y + self.y) / self.zoom
        return world_x, world_y
