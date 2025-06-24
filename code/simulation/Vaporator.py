from typing import ClassVar, Dict, Optional, List, Type, Optional
from pydantic import BaseModel
from simulation.Component import Chassis, ComponentSlot, Component, PowerPack, SmallPowerPack
from simulation.World import World

# --- Supporting Components for Vaporators ---

class CondenserUnit(Component):
    def on_tick(self, world: World):
        if not self.chassis:
            raise ValueError("CondenserUnit must be installed in a chassis to function.")
        
        tank = self.chassis.get_component(WaterTank)
        if not tank:
            print("No water tank found in the chassis. CondenserUnit cannot function without a water tank.")
            # TODO: Post an error message that the AI can see
            return

        power = self.chassis.get_component(PowerPack)
        if not power:
            print("No power pack found in the chassis. CondenserUnit cannot function without a power pack.")
            # TODO: Post an error message that the AI can see
            return

        if tank.fill >= tank.capacity:
            print("Water tank is full. CondenserUnit cannot condense more water.")
            # TODO: Post an error message to world and/or chassis system?
            return
        if power.charge <= 0:
            print("Power pack is empty. CondenserUnit cannot condense water.")
            # TODO: Post an error message to world and/or chassis system?
            return
            
        # Condense water
        # TODO: Condense less water if the Condensor is in poor condition
        # TODO: Condense more water if the Condensor has been tuned / adjusted recently
        power.charge -= 1
        tank.fill += 1

class WaterTank(Component):
    fill: int = 0
    capacity: int = 100

class SmallWaterTank(WaterTank):
    capacity: int = 50

class LargeWaterTank(WaterTank):
    capacity: int = 200

# --- Specific Equipment Types ---
# Similar to droids, Equipment can have a chassis that allows for components
#  to be installed or removed, providing modular functionality for a rich
#  simulation environment.

class Vaporator(Chassis):
    model: str = "GX-1"
    description: str = "A device used to extract moisture from the air, typically used in arid environments."
    
    slots: Dict[str, ComponentSlot] = {
        "power_pack": ComponentSlot(accepts=PowerPack, component=SmallPowerPack()),
        "condenser": ComponentSlot(accepts=CondenserUnit, component=CondenserUnit()),
        "water_tank": ComponentSlot(accepts=WaterTank, component=SmallWaterTank()),
    }

class GX8Vaporator(Vaporator):
    model: str = "GX-8"
    description: str = "An advanced vaporator with improved power capacity and a larger water tank. More efficient condensers can collect more water from the air."
    
    slots: Dict[str, ComponentSlot] = {
        "power_pack": ComponentSlot(accepts=PowerPack, component=PowerPack()),
        # TODO: Actually implement a more advanced CondenserUnit that can collect more water
        "condenser": ComponentSlot(accepts=CondenserUnit, component=CondenserUnit()),
        "water_tank": ComponentSlot(accepts=WaterTank, component=LargeWaterTank()),
    }