from typing import Dict

# --- Specific Droid Types ---
from simulation.core.entity.component.Component import (Chassis, Component,
                                                        ComponentSlot,
                                                        ComputerProbe,
                                                        PowerPack,
                                                        SmallPowerPack)
from simulation.core.entity.component.DroidAgentSimple import DroidAgentSimple
from simulation.core.entity.component.DroidAgentSimplePowerDroid import \
    DroidAgentSimplePowerDroid
from simulation.core.entity.component.DroidComponents import Motivator


class R2Astromech(Chassis):
    model:str = "R2 Astromech"

    slots: Dict[str, ComponentSlot] = {
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

    slots: Dict[str, ComponentSlot] = {
        "agent": ComponentSlot(accepts=DroidAgentSimple),
        "power_pack": ComponentSlot(accepts=PowerPack, component=PowerPack()),
        "motivator": ComponentSlot(accepts=Motivator, component=Motivator()),
        "misc": ComponentSlot(accepts=Component),  # For any additional components
    }
    
    def __init__(self, **data):
        super().__init__(**data)
        # Install default agent component after initialization
        if not self.slots["agent"].component:
            self.install_component("agent", DroidAgentSimplePowerDroid())

