from typing import Dict

from simulation.core.entity.Chassis import Chassis
from simulation.core.entity.component.PowerGenerator import PowerGenerator
from simulation.core.entity.component.PowerPack import (LargePowerPack,
                                                        PowerPack)
from simulation.core.entity.ComponentSlot import ComponentSlot
from simulation.equipment.PowerGeneratorModels import (MicroFusionPowerCell,
                                                       SolarPowerGenerator)

Chassis.model_rebuild()
LargePowerPack.model_rebuild()

class PowerStation(Chassis):
    model: str = "Generic Power Station"
    subtype: str = "power station"
    description: str = "A device used to extract moisture from the air, typically used in arid environments."
    
    slots: Dict[str, ComponentSlot] = {
        "power_pack": ComponentSlot(accepts=PowerPack),
        "power_generator": ComponentSlot(accepts=PowerGenerator),
    }

# Due to their symbiotic relationship with plants, M'shinn technology has two main foci - solar power and agriculture. The M'shinni have combined the sciences of engineering and botany in some unusual ways, producing solar collectors and power generators that are based on organic, cellular technologies.
class SolarPowerStation(PowerStation):
    model: str = "SPG-1"
    description: str = "A solar power generator that harnesses sunlight to produce energy."

    slots: Dict[str, ComponentSlot] = {
        "power_pack": ComponentSlot(accepts=PowerPack, default_component=LargePowerPack),
        "power_generator": ComponentSlot(accepts=PowerGenerator, default_component=SolarPowerGenerator),
    }

class MicroFusionPowerStation(PowerStation):
    model: str = "MN-5"
    description: str = "A micro fusion power station that uses advanced nuclear technology to generate energy."

    slots: Dict[str, ComponentSlot] = {
        "power_pack": ComponentSlot(accepts=PowerPack, default_component=LargePowerPack),
        "power_generator": ComponentSlot(accepts=PowerGenerator, default_component=MicroFusionPowerCell),
    }

# Girondium: A material combined with colium to manufacture ultra-high-efficiency solar cells, it was used by the Empire to make girondium-colium solar cells for the TIE bomber and later the TIE interceptor.

# These short-barreled lasers draw power from a single Novaldex generator at the rear of the central spar. The Novaldex Generator is a compact fusion reactor that provides power to the laser systems.

# I-a2b solar ionization reactor was a power system designed by Sienar Fleet Systems. They powered the TIE fighters,[1] although the I-s3a solar ionization reactor would also see use.[2]

# The I-s3a solar ionization reactor was a model of reactor used in Sienar Fleet Systems's TIE/ln space superiority starfighter to power a pair of P-s5.6 twin ion engines. Ship designer Raith Sienar also used this pairing in the prototype TIE Advanced x1 that he designed for the Sith Lord Darth Vader.
