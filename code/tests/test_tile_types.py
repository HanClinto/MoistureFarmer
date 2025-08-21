from simulation.entity.Tilemap import Tilemap
from simulation.entity.TileTypes import TileType

def test_tile_types_serialization():
    tm = Tilemap.from_default()
    j = tm.to_json()
    assert 'tile_types' in j
    # Default types present
    names = {tt['name'] for tt in j['tile_types'].values()}
    assert {'sand','rock','pad'}.issubset(names)

    # Register new type and reserialize
    ice = TileType(id=3, name='ice', passable=True, move_speed_scalar=1.2, can_mutate=True)
    tm.register_tile_type(ice)
    j2 = tm.to_json()
    assert '3' in j2['legend']
    assert j2['tile_types'][3]['name'] == 'ice'
