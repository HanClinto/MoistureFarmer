import pygame
import os
import sys
import pytmx
from camera import Camera
from typing import Optional

class TMXViewer:
    """Main application class for viewing TMX maps"""

    def __init__(self, tmx_path: str):
        pygame.init()

        # Screen setup
        self.screen_width = 1024
        self.screen_height = 768
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("TMX Viewer - Pan with WASD/Mouse, Zoom with Mousewheel")

        # Load TMX map
        self.tmx_data = self.load_tmx(tmx_path)
        if not self.tmx_data:
            sys.exit(1)

        # Camera setup
        self.camera = Camera(self.screen_width, self.screen_height)

        # Clock for frame rate
        self.clock = pygame.time.Clock()
        self.running = True

        # Mouse panning
        self.mouse_panning = False
        self.last_mouse_pos = (0, 0)

    def load_tmx(self, tmx_path: str) -> Optional[pytmx.TiledMap]:
        """Load and validate TMX file"""
        if not os.path.exists(tmx_path):
            print(f"Error: TMX file not found at {tmx_path}")
            return None

        try:
            tmx_data = pytmx.load_pygame(tmx_path)
            print(f"Loaded TMX: {tmx_data.width}x{tmx_data.height} tiles")
            print(f"Tile size: {tmx_data.tilewidth}x{tmx_data.tileheight}")
            print(f"Map size: {tmx_data.width * tmx_data.tilewidth}x{tmx_data.height * tmx_data.tileheight} pixels")
            print(f"Layers: {len(tmx_data.layers)}")

            # List layer names
            for i, layer in enumerate(tmx_data.layers):
                if hasattr(layer, 'name'):
                    print(f"  Layer {i}: {layer.name}")

            return tmx_data
        except Exception as e:
            print(f"Error loading TMX file: {e}")
            return None

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self.mouse_panning = True
                    self.last_mouse_pos = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    self.mouse_panning = False
            elif event.type == pygame.MOUSEMOTION:
                if self.mouse_panning:
                    current_pos = pygame.mouse.get_pos()
                    dx = current_pos[0] - self.last_mouse_pos[0]
                    dy = current_pos[1] - self.last_mouse_pos[1]
                    self.camera.x -= dx
                    self.camera.y -= dy
                    self.last_mouse_pos = current_pos
            elif event.type == pygame.MOUSEWHEEL:
                # Handle mousewheel zoom with discrete levels
                mouse_pos = pygame.mouse.get_pos()
                zoom_direction = 1 if event.y > 0 else -1  # Zoom in or out
                self.camera.zoom_at_point(zoom_direction, mouse_pos[0], mouse_pos[1])

    def render(self):
        """Render the map"""
        self.screen.fill((0, 0, 0))  # Black background

        if not self.tmx_data:
            return

        # Get visible tile range
        start_x, start_y, end_x, end_y = self.camera.get_visible_tiles(
            self.tmx_data.tilewidth,
            self.tmx_data.tileheight,
            self.tmx_data.width,
            self.tmx_data.height
        )
        # Render each layer
        for layer_index, layer in enumerate(self.tmx_data.layers):
            if hasattr(layer, 'data'):  # It's a tile layer
                self.render_tile_layer(layer_index, start_x, start_y, end_x, end_y)

        # Draw UI info
        self.draw_ui()

        pygame.display.flip()

    def render_tile_layer(self, layer_index: int, start_x: int, start_y: int, end_x: int, end_y: int):
        """Render a specific tile layer"""
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if 0 <= x < self.tmx_data.width and 0 <= y < self.tmx_data.height:
                    tile = self.tmx_data.get_tile_image(x, y, layer_index)
                    if tile:
                        # Calculate screen position with zoom
                        screen_x = x * self.tmx_data.tilewidth * self.camera.zoom - self.camera.x
                        screen_y = y * self.tmx_data.tileheight * self.camera.zoom - self.camera.y

                        # Scale tile if zoom is not 1.0
                        if self.camera.zoom != 1.0:
                            scaled_width = int(self.tmx_data.tilewidth * self.camera.zoom)
                            scaled_height = int(self.tmx_data.tileheight * self.camera.zoom)
                            tile = pygame.transform.scale(tile, (scaled_width, scaled_height))

                        self.screen.blit(tile, (screen_x, screen_y))

    def draw_ui(self):
        """Draw UI information"""
        font = pygame.font.Font(None, 24)

        # Camera position and zoom
        cam_text = f"Camera: ({int(self.camera.x)}, {int(self.camera.y)}) Zoom: {self.camera.zoom:.2f}"
        cam_surface = font.render(cam_text, True, (255, 255, 255))
        self.screen.blit(cam_surface, (10, 10))

        # Map info
        if self.tmx_data:
            map_text = f"Map: {self.tmx_data.width}x{self.tmx_data.height} tiles"
            map_surface = font.render(map_text, True, (255, 255, 255))
            self.screen.blit(map_surface, (10, 35))

        # Controls
        controls = [
            "Controls:",
            "WASD / Arrow Keys: Pan",
            "Mouse: Click and drag to pan",
            "Mouse Wheel: Zoom in/out",
            "ESC: Exit"
        ]

        for i, control in enumerate(controls):
            color = (255, 255, 0) if i == 0 else (200, 200, 200)
            control_surface = font.render(control, True, color)
            self.screen.blit(control_surface, (10, self.screen_height - 120 + i * 20))

    def run(self):
        """Main game loop"""
        print("Starting TMX Viewer...")
        print("Use WASD or arrow keys to pan around the map")
        print("Use mouse wheel to zoom in/out")
        print("Press ESC to exit")

        while self.running:
            dt = self.clock.tick(60) / 1000.0  # Delta time in seconds

            self.handle_events()

            # Update camera with keyboard input
            keys_pressed = pygame.key.get_pressed()
            self.camera.update(dt, keys_pressed)
            self.camera.clamp_to_tilemap(self.tmx_data.width, self.tmx_data.height, self.tmx_data.tilewidth, self.tmx_data.tileheight)

            self.render()

        pygame.quit()

def main():
    """Entry point"""
    # Path to TMX file - adjust as needed
    tmx_path = os.path.join("..", "resources", "tiles", "MAP_02.tmx")

    if not os.path.exists(tmx_path):
        print(f"TMX file not found at: {tmx_path}")
        print("Please check the path and try again.")
        sys.exit(1)

    viewer = TMXViewer(tmx_path)
    viewer.run()

if __name__ == "__main__":
    main()
