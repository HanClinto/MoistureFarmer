from typing import ClassVar, Dict, Optional, List, Type, Optional
from pydantic import BaseModel
from simulation.Component import Chassis, ComponentSlot, Component, Motivator, PowerPack, SmallPowerPack, ComputerProbe

# --- Specific Droid Types ---
class R2Astromech(Chassis):
    model:str = "R2 Astromech"

    slot: Dict[str, ComponentSlot] = {
        "processor": ComponentSlot(accepts=Component),
        "motivator": ComponentSlot(accepts=Motivator, component=Motivator()),
        "power_pack": ComponentSlot(accepts=PowerPack, component=SmallPowerPack()),
        "manipulator_1": ComponentSlot(accepts=Component),
        "manipulator_2": ComponentSlot(accepts=Component),
        "manipulator_3": ComponentSlot(accepts=Component),
        "manipulator_4": ComponentSlot(accepts=Component),
        "computer_probe": ComponentSlot(accepts=ComputerProbe, component=ComputerProbe())
    }

class GonkDroid(Chassis):
    model: str = "EG-6"
    subtype: str = "power droid"
    description: str = "A power droid designed to provide energy to other equipment. It has a limited battery capacity and can recharge itself at power stations."

    slot: Dict[str, ComponentSlot] = {
        "power_pack": ComponentSlot(accepts=PowerPack, component=PowerPack()),
        "motivator": ComponentSlot(accepts=Motivator, component=Motivator()),
    }

