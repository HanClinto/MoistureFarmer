import pygame
import os
import sys
import pytmx
from camera import Camera
from typing import Optional
from CollisionManager import CollisionManager

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
        
        # Center camera on CameraSpawn object
        self.center_camera_on_spawn()

        # Clock for frame rate
        self.clock = pygame.time.Clock()
        self.running = True

        # Mouse panning
        self.mouse_panning = False
        self.last_mouse_pos = (0, 0)

        # Initialize collision manager
        self.collision_manager = CollisionManager(self.tmx_data)

        # Very noisy collision debug output; disable by default.
        if False:
            # Log the number of blocking tiles once at TMX load
            self.collision_manager.log_blocking_tiles_count()

            # Log the histogram of blocking tiles once at TMX load
            self.collision_manager.log_blocking_tiles_histogram()

        # Allocate a single font for the class
        self.font_32pt = pygame.font.Font(None, 32)
        self.font_20pt = pygame.font.Font(None, 20)

    def load_tmx(self, tmx_path: str) -> Optional[pytmx.TiledMap]:
        """Load and validate TMX file"""
        if not os.path.exists(tmx_path):
            print(f"Error: TMX file not found at {tmx_path}")
            return None

        try:
            tmx_data = pytmx.load_pygame(tmx_path, None, load_all=True, allow_duplicate_names=True)
            print(f"Loaded TMX: {tmx_data.width}x{tmx_data.height} tiles")
            print(f"Tile size: {tmx_data.tilewidth}x{tmx_data.tileheight}")
            print(f"Map size: {tmx_data.width * tmx_data.tilewidth}x{tmx_data.height * tmx_data.tileheight} pixels")
            print(f"Layers: {len(tmx_data.layers)}")

            # List layer names, types, and object counts for TiledObjectGroup layers
            for i, layer in enumerate(tmx_data.layers):
                layer_type = type(layer).__name__
                if hasattr(layer, 'name'):
                    layer_name = layer.name
                else:
                    layer_name = "Unnamed"

                if isinstance(layer, pytmx.TiledObjectGroup):
                    object_count = len(layer)
                    print(f"  Layer {i}: {layer_name} (Type: {layer_type}, Objects: {object_count})")
                else:
                    print(f"  Layer {i}: {layer_name} (Type: {layer_type})")

            return tmx_data
        except Exception as e:
            print(f"Error loading TMX file: {e}")
            return None

    def center_camera_on_spawn(self):
        """Find the CameraSpawn object and center the camera on it"""
        if not self.tmx_data:
            return
            
        for layer in self.tmx_data.layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                for obj in layer:
                    if obj.name == "CameraSpawn":
                        # Center the camera on the spawn point
                        # Account for zoom and screen center offset
                        self.camera.x = obj.x * self.camera.zoom - self.screen_width // 2
                        self.camera.y = obj.y * self.camera.zoom - self.screen_height // 2
                        print(f"Camera centered on CameraSpawn at world ({obj.x}, {obj.y}) with zoom {self.camera.zoom}")
                        return
        
        print("Warning: CameraSpawn object not found in TMX file")

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_c:
                    # Toggle collision rendering
                    self.collision_manager.toggle_rendering()
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

    def render_objects(self):
        """Render objects from the TMX map"""
        if not self.tmx_data:
            return 0

        drawn_objects = 0
        for layer in self.tmx_data.layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                for obj in layer:
                    # Render all objects, not just those with type "point"
                    screen_x, screen_y = self.camera.world_to_screen(obj.x, obj.y)

                    # Draw a small red rectangle for the object
                    rect_size = 5
                    pygame.draw.rect(
                        self.screen,
                        (255, 0, 0),  # Red color
                        pygame.Rect(
                            screen_x - rect_size // 2,
                            screen_y - rect_size // 2,
                            rect_size,
                            rect_size
                        )
                    )

                    # Draw the object's ID/name above the rectangle
                    obj_name = obj.name or obj.id
                    text_surface = self.font_20pt.render(str(obj_name), True, (255, 255, 255))
                    self.screen.blit(text_surface, (screen_x - text_surface.get_width() // 2, screen_y - 20))

                    drawn_objects += 1

        return drawn_objects

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
        total_drawn_tiles = 0
        # Render each layer
        for layer_index, layer in enumerate(self.tmx_data.layers):
            if hasattr(layer, 'data'):  # It's a tile layer
                total_drawn_tiles += self.render_tile_layer(layer_index, start_x, start_y, end_x, end_y)

        # Render point objects (ensure they are drawn above the tilemap)
        total_drawn_objects = self.render_objects()

        # Render blocking tiles if toggled
        self.collision_manager.render(self.screen, self.camera)

        # Draw UI info
        self.draw_ui(total_drawn_tiles, total_drawn_objects)

        pygame.display.flip()

    def render_tile_layer(self, layer_index: int, start_x: int, start_y: int, end_x: int, end_y: int):
        """Render a specific tile layer"""
        drawn_tiles = 0
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if 0 <= x < self.tmx_data.width and 0 <= y < self.tmx_data.height:
                    tile = self.tmx_data.get_tile_image(x, y, layer_index)
                    if tile:
                        # Use camera's world_to_screen for position calculation
                        screen_x, screen_y = self.camera.world_to_screen(x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight)

                        # Scale tile if zoom is not 1.0
                        if self.camera.zoom != 1.0:
                            scaled_width = int(self.tmx_data.tilewidth * self.camera.zoom)
                            scaled_height = int(self.tmx_data.tileheight * self.camera.zoom)
                            tile = pygame.transform.scale(tile, (scaled_width, scaled_height))

                        # Ensure transparency for Foreground layer tiles
                        if self.tmx_data.layers[layer_index].name == "Foreground":
                            tile.set_colorkey((0, 0, 0))

                        self.screen.blit(tile, (screen_x, screen_y))
                        drawn_tiles += 1

        return drawn_tiles

    def draw_ui(self, total_drawn_tiles, total_drawn_objects):
        """Draw UI information"""
        font = self.font_32pt

        # Camera position and zoom
        cam_text = f"Camera: ({int(self.camera.x)}, {int(self.camera.y)}) Zoom: {self.camera.zoom:.2f}"
        cam_surface = font.render(cam_text, True, (255, 255, 255))
        self.screen.blit(cam_surface, (10, 10))

        # Map info
        if self.tmx_data:
            map_text = f"Map: {self.tmx_data.width}x{self.tmx_data.height} tiles"
            map_surface = font.render(map_text, True, (255, 255, 255))
            self.screen.blit(map_surface, (10, 35))

        # Number of drawn tiles
        drawn_tiles_text = f"Drawn Tiles: {total_drawn_tiles}"
        drawn_tiles_surface = font.render(drawn_tiles_text, True, (255, 255, 255))
        self.screen.blit(drawn_tiles_surface, (10, 60))

        # Number of drawn point objects
        drawn_objects_text = f"Drawn Objects: {total_drawn_objects}"
        drawn_objects_surface = font.render(drawn_objects_text, True, (255, 255, 255))
        self.screen.blit(drawn_objects_surface, (10, 85))

        # Display collision render status
        font = self.font_32pt
        text = font.render(f"Collision Render: {'ON' if self.collision_manager.render_blocking_tiles else 'OFF'}", True, (255, 255, 255))
        self.screen.blit(text, (10, 110))

        # Controls
        controls = [
            "Controls:",
            "Mouse: Drag to pan, wheel to zoom",
            "ESC: Exit     C: Toggle Collision Rendering"
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
        print("Press C to toggle collision rendering")

        while self.running:
            dt = self.clock.tick(60) / 1000.0  # Delta time in seconds

            self.handle_events()

            # Update camera with keyboard input
            keys_pressed = pygame.key.get_pressed()
            self.camera.update(dt, keys_pressed)
            self.camera.clamp_to_tilemap(self.tmx_data.width, self.tmx_data.height, self.tmx_data.tilewidth, self.tmx_data.tileheight)

            self.render()

        pygame.quit()
