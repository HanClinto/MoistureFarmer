from typing import Dict

from simulation.core.entity.Chassis import Chassis
from simulation.core.entity.component.CondenserUnit import (
    AdvancedCondenserUnit, CondenserUnit)
from simulation.core.entity.component.PowerPack import (PowerPack,
                                                        SmallPowerPack)
from simulation.core.entity.component.WaterTank import WaterTank
from simulation.core.entity.ComponentSlot import ComponentSlot
from simulation.core.entity.Vaporator import Vaporator
from simulation.equipment.WaterTankModels import LargeWaterTank, SmallWaterTank

Chassis.model_rebuild()
LargeWaterTank.model_rebuild()
SmallWaterTank.model_rebuild()
CondenserUnit.model_rebuild()
AdvancedCondenserUnit.model_rebuild()

class GX1_Vaporator(Vaporator):
    model: str = "GX-1"
    
    slots: Dict[str, ComponentSlot] = {
        "power_pack": ComponentSlot(accepts=PowerPack, default_component=SmallPowerPack),
        "condenser": ComponentSlot(accepts=CondenserUnit, default_component=CondenserUnit),
        "water_tank": ComponentSlot(accepts=WaterTank, default_component=SmallWaterTank),
    }

class GX8_Vaporator(Vaporator):
    model: str = "GX-8"
    description: str = "An advanced vaporator with improved power capacity and a larger water tank. More efficient condensers can collect more water from the air."

    slots: Dict[str, ComponentSlot] = {
        "power_pack": ComponentSlot(accepts=PowerPack, default_component=PowerPack),
        "condenser": ComponentSlot(accepts=CondenserUnit, default_component=AdvancedCondenserUnit),
        "water_tank": ComponentSlot(accepts=WaterTank, default_component=LargeWaterTank),
    }
