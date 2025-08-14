from simulation.World import World
from simulation.Tilemap import Tilemap
from simulation.TileMapEntity import TileMapEntity
from simulation.Entity import Location

class DummyMover(TileMapEntity):
    # Use standard Python attributes set post-init (pydantic allows undeclared if model_config extra='allow', but here we set after)
    def __init__(self, **data):
        super().__init__(**data)
        object.__setattr__(self, 'collisions', [])
        object.__setattr__(self, 'move_failed', [])
        object.__setattr__(self, 'moved', [])
    def on_collided(self, other, initiated: bool):
        self.collisions.append((other.id, initiated))
    def on_move_failed(self, reason: str, attempted):
        self.move_failed.append((reason, attempted))
    def on_moved(self, from_loc, to_loc):
        self.moved.append((from_loc.x, from_loc.y, to_loc.x, to_loc.y))


def run_one_tick(world: World):
    world.tick()


def test_simple_move_success():
    w = World()
    w.tilemap = Tilemap.from_default()
    a = DummyMover(location=Location(x=10,y=10))
    w.add_entity(a)
    a.set_pending_move(1,0)
    run_one_tick(w)
    assert a.location.x == 11 and a.location.y == 10
    assert any(entry['id']==a.id and entry['status']=='moved' for entry in w.last_movement_journal)


def test_blocked_by_impassable_tile():
    w = World()
    w.tilemap = Tilemap.from_default()
    # Place entity next to border rock (impassable) and attempt to move into it
    a = DummyMover(location=Location(x=1,y=0))  # top row y=0 is rock border, so place just below instead
    a.location = Location(x=1,y=1)  # inside map
    w.add_entity(a)
    a.set_pending_move(-1,0)  # moving left into border rock at x=0
    run_one_tick(w)
    assert a.location.x == 1  # no move
    entry = next(e for e in w.last_movement_journal if e['id']==a.id)
    assert entry['status'] == 'blocked_tile'


def test_entity_collision_blocks_second():
    w = World()
    w.tilemap = Tilemap.from_default()
    a = DummyMover(location=Location(x=5,y=5), priority=50)
    b = DummyMover(location=Location(x=6,y=5), priority=100)
    w.add_entity(a)
    w.add_entity(b)
    # a moves right into b's current tile; b stays
    a.set_pending_move(1,0)
    run_one_tick(w)
    # a should be blocked by b (entity collision)
    assert a.location.x == 5
    entry_a = next(e for e in w.last_movement_journal if e['id']==a.id)
    assert entry_a['status'] == 'blocked_entity'


def test_out_of_bounds_block():
    w = World()
    w.tilemap = Tilemap.from_default()
    # Place near right edge and attempt to move outside
    edge_x = w.tilemap.width - 1
    a = DummyMover(location=Location(x=edge_x-0,y=10))
    w.add_entity(a)
    a.set_pending_move(1,0)
    run_one_tick(w)
    assert a.location.x == edge_x
    entry = next(e for e in w.last_movement_journal if e['id']==a.id)
    assert entry['status'] == 'blocked_tile'


def test_journal_no_pending():
    w = World()
    w.tilemap = Tilemap.from_default()
    a = DummyMover(location=Location(x=10,y=10))
    w.add_entity(a)
    run_one_tick(w)
    entry = next(e for e in w.last_movement_journal if e['id']==a.id)
    assert entry['status'] == 'no_pending'
