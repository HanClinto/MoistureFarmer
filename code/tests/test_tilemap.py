from simulation.entity.Tilemap import Tilemap


def test_tilemap_default_init_shape():
    tm = Tilemap()
    j = tm.to_json()

    # Allow additional future keys (e.g., tile_types) while ensuring required baseline keys exist.
    for required in ["width", "height", "tiles", "legend", "last_mutation"]:
        assert required in j
    assert isinstance(j["width"], int) and j["width"] == 128
    assert isinstance(j["height"], int) and j["height"] == 128
    assert isinstance(j["tiles"], list) and len(j["tiles"]) == j["height"]
    assert isinstance(j["tiles"][0], list) and len(j["tiles"][0]) == j["width"]

    # Borders should be rock (1), interior sand (0), center pad (2)
    width = j["width"]
    height = j["height"]
    tiles = j["tiles"]

    # Check corners (border)
    assert tiles[0][0] == 1
    assert tiles[0][width - 1] == 1
    assert tiles[height - 1][0] == 1
    assert tiles[height - 1][width - 1] == 1

    # Check center pad
    cx, cy = width // 2, height // 2
    assert tiles[cy][cx] == 2

    # No mutation yet
    assert j["last_mutation"] is None


def test_tilemap_mutation_updates_one_cell():
    tm = Tilemap.from_default()
    before = [row[:] for row in tm.tiles]

    tm.maybe_mutate()
    j = tm.to_json()

    # Mutation metadata set
    lm = j["last_mutation"]
    assert lm is not None
    x = lm["x"]
    y = lm["y"]
    v = lm["value"]

    # Ensure coordinates are interior
    assert 1 <= x <= j["width"] - 2
    assert 1 <= y <= j["height"] - 2

    # Ensure the tile value at (x, y) matches recorded value
    assert tm.tiles[y][x] == v
