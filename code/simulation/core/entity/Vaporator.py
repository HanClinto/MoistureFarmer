from typing import Dict

from simulation.core.entity.component.Component import Chassis, ComponentSlot
from simulation.core.entity.component.CondenserUnit import CondenserUnit
from simulation.core.entity.component.PowerPack import PowerPack
from simulation.core.entity.component.WaterTank import WaterTank

# --- Specific Equipment Types ---
# Similar to droids, Equipment can have a chassis that allows for components
#  to be installed or removed, providing modular functionality for a rich
#  simulation environment.

class Vaporator(Chassis):
    model: str = "Generic Vaporator"
    description: str = "A device used to extract moisture from the air, typically used in arid environments."
    
    slots: Dict[str, ComponentSlot] = {
        "power_pack": ComponentSlot(accepts=PowerPack),
        "condenser": ComponentSlot(accepts=CondenserUnit),
        "water_tank": ComponentSlot(accepts=WaterTank),
    }
