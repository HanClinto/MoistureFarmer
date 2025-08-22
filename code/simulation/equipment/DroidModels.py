from typing import Dict

# --- Specific Droid Types ---
from simulation.core.entity.component.Chassis import Chassis
from simulation.core.entity.component.Component import Component
from simulation.core.entity.component.ComponentSlot import ComponentSlot
from simulation.core.entity.component.ComputerProbe import ComputerProbe
from simulation.core.entity.component.Motivator import Motivator
from simulation.core.entity.component.PowerPack import (PowerPack,
                                                        SmallPowerPack)
from simulation.equipment.DroidAgentModels import (DroidAgentSimple,
                                                   DroidAgentSimplePowerDroid)


class R2Astromech(Chassis):
    model:str = "R2 Astromech"

    slots: Dict[str, ComponentSlot] = {
        "processor": ComponentSlot(accepts=Component),
        "motivator": ComponentSlot(accepts=Motivator, default_component=Motivator),
        "power_pack": ComponentSlot(accepts=PowerPack, default_component=SmallPowerPack),
        "manipulator_1": ComponentSlot(accepts=Component),
        "manipulator_2": ComponentSlot(accepts=Component),
        "manipulator_3": ComponentSlot(accepts=Component),
        "manipulator_4": ComponentSlot(accepts=Component),
        "computer_probe": ComponentSlot(accepts=ComputerProbe, default_component=ComputerProbe)
    }

class GonkDroid(Chassis):
    model: str = "EG-6"
    subtype: str = "power droid"
    description: str = "A power droid designed to provide energy to other equipment. It has a limited battery capacity and can recharge itself at power stations."

    slots: Dict[str, ComponentSlot] = {
        "agent": ComponentSlot(accepts=DroidAgentSimple),
        "power_pack": ComponentSlot(accepts=PowerPack, default_component=PowerPack),
        "motivator": ComponentSlot(accepts=Motivator, default_component=Motivator),
        "misc": ComponentSlot(accepts=Component),  # For any additional components
    }
    
    def __init__(self, **data):
        super().__init__(**data)
        # Install default agent component after initialization
        if not self.slots["agent"].component:
            self.install_component("agent", DroidAgentSimplePowerDroid())

