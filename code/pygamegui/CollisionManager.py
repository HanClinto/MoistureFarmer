import pygame

class CollisionManager:
    def __init__(self, tilemap):
        self.tilemap = tilemap
        self.render_blocking_tiles = False

    def is_tile_blocking(self, x, y):
        foreground_layer_index = 0  # Assuming foreground is the first layer
        background_layer_index = 1  # Assuming background is the second layer

        # Check the collide property for both foreground and background tiles by GID.
        foreground_props = self.tilemap.get_tile_properties(x, y, foreground_layer_index)
        background_props = self.tilemap.get_tile_properties(x, y, background_layer_index)

        isCollider = False
        if foreground_props is not None:
            isCollider = foreground_props.get('collide', False)
        if isCollider is False and background_props is not None:
            isCollider = background_props.get('collide', False)

        return isCollider

    def get_blocking_tiles(self):
        blocking_tiles = []

        for x in range(self.tilemap.width):
            for y in range(self.tilemap.height):
                if self.is_tile_blocking(x, y):
                    blocking_tiles.append({'x': x, 'y': y})

        return blocking_tiles

    def toggle_rendering(self):
        self.render_blocking_tiles = not self.render_blocking_tiles

    def render(self, screen, camera):
        if self.render_blocking_tiles:
            blocking_tiles = self.get_blocking_tiles()
            for tile in blocking_tiles:
                x, y = tile['x'], tile['y']
                world_x = x * self.tilemap.tilewidth
                world_y = y * self.tilemap.tileheight
                screen_x, screen_y = camera.world_to_screen(world_x, world_y)
                rect = pygame.Rect(screen_x, screen_y, self.tilemap.tilewidth * camera.zoom, self.tilemap.tileheight * camera.zoom)
                pygame.draw.rect(screen, (255, 0, 0, 32), rect)  # Red transparent rectangle

    def log_blocking_tiles_count(self):
        blocking_tiles = []
        for layer_index, layer in enumerate(self.tilemap.layers):
            if hasattr(layer, 'data'):  # Ensure it's a tile layer
                for x in range(self.tilemap.width):
                    for y in range(self.tilemap.height):
                        tile_gid = self.tilemap.get_tile_gid(x, y, layer_index)  # Use layer index
                        if tile_gid in self.block_tile_ids:
                            blocking_tiles.append({'x': x, 'y': y})
        print(f"Number of blocking tiles: {len(blocking_tiles)}")

    def log_blocking_tiles_histogram(self):
        tile_counts = {tile_id: 0 for tile_id in self.block_tile_ids}

        print("GID (tile) properties:")
        for k, v in self.tilemap.tile_properties.items():
            print(f"{k} = {v}")

        print("Tile colliders:")
        for k, v in self.tilemap.get_tile_colliders():
            print(f"{k} = {v}")

        for layer_index, layer in enumerate(self.tilemap.layers):
            if hasattr(layer, 'data'):  # Ensure it's a tile layer
                print(f"Processing layer {layer_index}: {layer.name}")  # Debugging statement
                for x in range(self.tilemap.width):
                    for y in range(self.tilemap.height):
                        tile_gid = self.tilemap.get_tile_gid(x, y, layer_index)  # Use layer index
                        tile_props = self.tilemap.get_tile_properties(x, y, layer_index)
                        tile_props2 = self.tilemap.get_tile_properties_by_gid(tile_gid)

                        # Map tile_gid to tile_id using tilesets
                        tile_id = None
                        for tileset in self.tilemap.tilesets:
                            if tileset.firstgid <= tile_gid < tileset.firstgid + tileset.tilecount:
                                tile_id = tile_gid - tileset.firstgid
                                break

                        if tile_id is not None and int(tile_id) > 0:
                            print(f"Tile at ({x}, {y}) in layer {layer_index}: GID {tile_gid}, ID {int(tile_id)}")  # Debugging statement

                        if tile_id in tile_counts:
                            tile_counts[tile_id] += 1

        print("Blocking Tiles Histogram:")
        for tile_id, count in tile_counts.items():
            if count > 0:
                print(f"Tile ID {tile_id}: {count} instances")
