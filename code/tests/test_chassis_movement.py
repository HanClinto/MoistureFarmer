import pytest
from simulation.core.entity.component.Chassis import Chassis, ComponentSlot
from simulation.core.entity.component.Motivator import Motivator
from simulation.core.entity.component.PowerPack import PowerPack
from simulation.core.entity.Entity import Location
from simulation.core.entity.Tilemap import Tilemap
from simulation.core.World import World


class SimpleChassis(Chassis):
    from typing import Dict as _Dict
    slots: dict[str, ComponentSlot] = {
        "motivator": ComponentSlot(accepts=Motivator, default_component=Motivator),
        "power": ComponentSlot(accepts=PowerPack, default_component=PowerPack),
    }

@pytest.fixture
def world():
    w = World()
    w.tilemap = Tilemap.from_default()
    return w

def test_simple_move_success(world):
    c = SimpleChassis(location=Location(x=10,y=10))
    world.add_entity(c)
    # Set a destination one step away
    motivator: Motivator = c.get_component(Motivator)  # type: ignore
    motivator.destination = Location(x=11,y=10)
    world.tick()  # motivator issues intent
    world.tick()  # movement resolves and second tick may clear destination
    assert (c.location.x, c.location.y) == (11,10)


def test_blocked_by_impassable_tile(world):
    # Place next to rock border (y=1 just under border, moving up into y=0 which is rock)
    c = SimpleChassis(location=Location(x=5,y=1))
    world.add_entity(c)
    motivator: Motivator = c.get_component(Motivator)  # type: ignore
    motivator.destination = Location(x=5,y=0)
    world.tick()
    world.tick()
    assert (c.location.x, c.location.y) == (5,1)


def test_entity_conflict(world):
    a = SimpleChassis(location=Location(x=5,y=5))
    b = SimpleChassis(location=Location(x=6,y=5))
    a.move_priority = 50
    b.move_priority = 100
    world.add_entity(a)
    world.add_entity(b)
    # a wants to move into b's tile; b stays
    mot_a: Motivator = a.get_component(Motivator)  # type: ignore
    mot_a.destination = Location(x=6,y=5)
    world.tick()
    world.tick()
    # Should remain blocked
    assert (a.location.x, a.location.y) == (5,5)


def test_out_of_bounds(world):
    edge_x = world.tilemap.width - 1
    c = SimpleChassis(location=Location(x=edge_x, y=10))
    world.add_entity(c)
    mot: Motivator = c.get_component(Motivator)  # type: ignore
    mot.destination = Location(x=edge_x+1, y=10)
    world.tick()
    world.tick()
    assert c.location.x == edge_x


def test_power_consumption_on_success(world):
    c = SimpleChassis(location=Location(x=10,y=10))
    world.add_entity(c)
    power: PowerPack = c.get_component(PowerPack)  # type: ignore
    start = power.charge
    mot: Motivator = c.get_component(Motivator)  # type: ignore
    mot.destination = Location(x=11,y=10)
    world.tick()
    world.tick()
    assert power.charge == start - 1


def test_priority_tie_break(world):
    c1 = make_chassis("A", world, 1, 1)
    c2 = make_chassis("B", world, 2, 1)
    # Same priority default 0; both move to the right into same target tile (2,1) from (1,1) and (2,1)?? Adjust positions to create contention.
    c1.location = Location(x=1, y=1)
    c2.location = Location(x=3, y=1)
    # c1 moves +1 to (2,1); c2 moves -1 to (2,1) simultaneous
    c1.request_move(1, 0)
    c2.request_move(-1, 0)
    world.resolve_movement()
    # Deterministic ordering by id should allow chassis with lexicographically smaller id to win
    assert (c1.location.x, c1.location.y) == (2, 1)
    assert (c2.location.x, c2.location.y) == (3, 1)


def test_invalid_intent(world):
    c1 = make_chassis("C", world)
    # Create an invalid intent (dx too large) - depending on validate constraints (assuming only -1..1 allowed)
    c1.request_move(5, 0)  # invalid
    world.resolve_movement()
    # Position unchanged
    assert (c1.location.x, c1.location.y) == (1, 1)


def make_chassis(id_val: str, world: World, x: int = 1, y: int = 1):
    c = SimpleChassis(id=id_val, location=Location(x=x,y=y))
    world.add_entity(c)
    return c


def test_cooldown_enforced(world):
    c = SimpleChassis(location=Location(x=10,y=10))
    world.add_entity(c)
    mot: Motivator = c.get_component(Motivator)  # type: ignore
    mot.destination = Location(x=12,y=10)
    # First tick: intent issued
    world.tick()
    # Second tick: move resolves (step 1)
    world.tick()
    first_pos = (c.location.x, c.location.y)
    assert first_pos == (11,10)
    # Third tick: cooldown tick, no new intent issued
    world.tick()
    assert (c.location.x, c.location.y) == (11,10)
    # Fourth tick: next intent issued
    world.tick()
    # Fifth tick: second move resolves
    world.tick()
    assert (c.location.x, c.location.y) == (12,10)


def test_power_not_consumed_on_block(world):
    c = SimpleChassis(location=Location(x=5,y=1))
    world.add_entity(c)
    power: PowerPack = c.get_component(PowerPack)  # type: ignore
    start = power.charge
    mot: Motivator = c.get_component(Motivator)  # type: ignore
    mot.destination = Location(x=5,y=0)  # blocked by rock border
    world.tick(); world.tick()
    assert power.charge == start


def test_duplicate_intent_rejected(world):
    c = SimpleChassis(location=Location(x=10,y=10))
    world.add_entity(c)
    ok1 = c.request_move(1,0)
    ok2 = c.request_move(0,1)
    assert ok1 is True and ok2 is False
    world.resolve_movement()
    # Only first intent applied
    assert (c.location.x, c.location.y) == (11,10)


def test_multitile_footprint_collision(world):
    # Create two chassis with 2x1 footprint moving into same space horizontally
    class WideChassis(SimpleChassis):
        footprint_w: int = 2
        footprint_h: int = 1
    a = WideChassis(id="WA", location=Location(x=2,y=2))
    b = WideChassis(id="WB", location=Location(x=5,y=2))
    world.add_entity(a); world.add_entity(b)
    # Request moves toward center
    a.request_move(1,0)  # occupies (2,2)(3,2) -> wants (3,2)(4,2)
    b.request_move(-1,0) # occupies (5,2)(6,2) -> wants (4,2)(5,2)
    world.resolve_movement()
    # One should succeed based on id ordering; check no overlap post move
    tiles_a = set(a.occupied_tiles())
    tiles_b = set(b.occupied_tiles())
    assert tiles_a.isdisjoint(tiles_b)


def test_multitile_out_of_bounds(world):
    class TallChassis(SimpleChassis):
        footprint_w: int = 1
        footprint_h: int = 2
    edge_y = world.tilemap.height - 1
    c = TallChassis(id="TC", location=Location(x=3, y=edge_y-1))
    world.add_entity(c)
    c.request_move(0,1)  # would extend beyond map
    world.resolve_movement()
    # Should not move
    assert (c.location.x, c.location.y) == (3, edge_y-1)
