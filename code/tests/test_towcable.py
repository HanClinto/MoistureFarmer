import pytest
from simulation.core.World import World
from simulation.core.entity.Entity import Location
from simulation.core.entity.Chassis import Chassis
from simulation.core.entity.ComponentSlot import ComponentSlot
from simulation.core.entity.component.Component import Component
from simulation.core.entity.component.CondenserUnit import CondenserUnit
from simulation.core.entity.component.Gripper import Gripper
from simulation.core.entity.component.PowerPack import PowerPack, SmallPowerPack
from simulation.core.entity.component.Storage import LargeStorage, Storage, SmallStorage
from simulation.core.entity.component.Motivator import Motivator
from simulation.core.entity.component.TowCable import TowCable
from simulation.equipment.WaterTankModels import LargeWaterTank, SmallWaterTank
from simulation.llm.ToolCall import ToolCallState

# Force model rebuild for components to fix forward reference issues
World.model_rebuild()
Chassis.model_rebuild()
ComponentSlot.model_rebuild()
Component.model_rebuild()
Storage.model_rebuild()
Gripper.model_rebuild()
CondenserUnit.model_rebuild()
PowerPack.model_rebuild()
SmallPowerPack.model_rebuild()
SmallStorage.model_rebuild()
LargeStorage.model_rebuild()
TowCable.model_rebuild()
Motivator.model_rebuild()
LargeWaterTank.model_rebuild()
SmallWaterTank.model_rebuild()

from simulation.equipment.DroidModels import R2Astromech
from simulation.equipment.VaporatorModels import GX1_Vaporator

R2Astromech.model_rebuild()
GX1_Vaporator.model_rebuild()

class TestTowCable:
    def setup_method(self):
        """Create a fresh world for each test."""
        self.world = World()

    def _setup_single_pull(self):
        # R2 at 5,5 with TowCable in misc slot
        r2 = R2Astromech(id="r2_1", location=Location(x=5, y=5))
        tow = TowCable()
        # R2 has several manipulator slots; use manipulator_1
        r2.install_component("manipulator_1", tow)

        # Vaporator adjacent at 5,6
        vap = GX1_Vaporator(id="vap_1", location=Location(x=5, y=6))

        # Add to world
        self.world.add_entity(r2)
        self.world.add_entity(vap)

        return r2, tow, vap

    def test_tow_single_pull_moves_vaporator(self):
        """Single R2 pulls a vaporator while moving east."""
        r2, tow, vap = self._setup_single_pull()

        # Attach tow cable to vaporator
        result = tow.attach_tow_cable(vap.id)
        assert result.state == ToolCallState.SUCCESS
        assert tow.attached_entity is vap

        # Tell motivator to move to 10,5
        motivator = r2.get_component(Motivator)
        assert motivator is not None
        call = motivator.move_to_location(10, 5)
        assert call.state == ToolCallState.IN_PROCESS

        # First tick: apply movement intents (none yet), then droids think and issue intent
        self.world.tick()
        print(f'Tick 1: R2 Location: {r2.location} (intent: {r2.pending_intent}), Vaporator Location: {vap.location} (intent: {vap.pending_intent})')
        # After first world.tick, movement intents applied from previous tick move nothing, but motivator should have issued a move intent.
        # Now resolve movement on next tick: r2 should move one tile to the right (6,5)
        self.world.tick()
        print(f'Tick 2: R2 Location: {r2.location} (intent: {r2.pending_intent}), Vaporator Location: {vap.location} (intent: {vap.pending_intent})')
        self.world.tick()
        print(f'Tick 3: R2 Location: {r2.location} (intent: {r2.pending_intent}), Vaporator Location: {vap.location} (intent: {vap.pending_intent})')
        self.world.tick()
        print(f'Tick 4: R2 Location: {r2.location} (intent: {r2.pending_intent}), Vaporator Location: {vap.location} (intent: {vap.pending_intent})')
        assert r2.location.x == 6 and r2.location.y == 5
        # Vaporator should have been pulled into the R2's previous position (5,5)
        assert vap.location.x == 5 and vap.location.y == 5

        # Tick 50 more times to allow r2 to reach (10,5)
        for _ in range(50):
            self.world.tick()

        assert r2.location.x == 10 and r2.location.y == 5
        # Vaporator should still be attached and trailing (one tile behind)
        assert vap.location.x == 9 and vap.location.y == 5
        assert tow.attached_entity is vap

    def test_tow_breaks_when_other_droid_blocks(self):
        """If a second droid moves into the vacated tile simultaneously, the tow should break."""
        # Setup primary r2 and vap
        r2, tow, vap = self._setup_single_pull()

        # Add second R2 at 4,5 which will attempt to move into 5,5 when r2 moves out
        other = R2Astromech(id="r2_2", location=Location(x=4, y=5))
        self.world.add_entity(other)

        # Attach tow cable to vaporator
        result = tow.attach_tow_cable(vap.id)
        assert result.state == ToolCallState.SUCCESS
        assert tow.attached_entity is vap

        # Both motivators move: r2 -> 10,5; other -> 5,5 (move east)
        motivator1 = r2.get_component(Motivator)
        motivator2 = other.get_component(Motivator)
        assert motivator1 and motivator2
        motivator1.move_to_location(10, 5)
        motivator2.move_to_location(5, 5)

        # First tick: issue intents
        self.world.tick()
        # Second tick: apply movement - both will attempt to move; r2 moves to 6,5 and will attempt to pull vap into 5,5
        # other will move from 4,5 to 5,5, causing occupancy conflict which should break the tow
        self.world.tick()

        # r2 should have moved to 6,5
        assert r2.location.x == 6 and r2.location.y == 5
        # The vaporator should NOT have been pulled; it should remain at original location 5,6 and no longer be attached
        assert vap.location.x == 5 and vap.location.y == 6
        assert tow.attached_entity is None
