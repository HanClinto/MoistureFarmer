import pytest
from simulation.core.entity.Chassis import Chassis
from simulation.core.entity.ComponentSlot import ComponentSlot
from simulation.core.entity.component.Motivator import Motivator
from simulation.core.entity.component.PowerPack import PowerPack
from simulation.core.entity.Entity import Location
from simulation.core.tiles.Tilemap import Tilemap
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


def make_chassis(id_val: str, world: World, x: int = 1, y: int = 1):
    c = SimpleChassis(id=id_val, location=Location(x=x,y=y))
    world.add_entity(c)
    return c


def test_cooldown_enforced(world):
    c = SimpleChassis(location=Location(x=10,y=10))
    world.add_entity(c)
    mot: Motivator = c.get_component(Motivator)  # type: ignore
    mot.destination = Location(x=12,y=10)
    # First tick: movement
    world.tick()
    assert (c.location.x, c.location.y) == (11,10)
    # Second tick: cooldown 1
    world.tick()
    assert (c.location.x, c.location.y) == (11,10)
    # Third tick: movement 2
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

