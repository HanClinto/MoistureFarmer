import pytest

# Ensure modules import without forward-ref errors and RandomWalker can be instantiated and ticked.

def test_random_walker_instantiation_and_tick():
    from simulation.core.Simulation import Simulation
    from simulation.core.entity.RandomWalker import RandomWalker
    from simulation.core.entity.Entity import Location

    # Explicit rebuild should be a no-op if already resolved; will raise if still invalid
    RandomWalker.model_rebuild()

    sim = Simulation(paused=True)  # paused so run loop won't advance automatically
    # Force tilemap init
    sim.world.tilemap = sim.world.tilemap or None
    # Instantiate walker (should not raise)
    walker = RandomWalker(id="rw_test", location=Location(x=10, y=10))
    sim.world.add_entity(walker)

    # Single manual world tick should execute walker.tick without forward-ref warnings being raised as exceptions
    sim.world.tick()

    # Validate walker present and has a valid location inside bounds
    assert walker.id in sim.world.entities
    assert 0 <= walker.location.x < sim.world.tilemap.width
    assert 0 <= walker.location.y < sim.world.tilemap.height
