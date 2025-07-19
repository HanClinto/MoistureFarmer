
from typing import Dict
# --- Specific Droid Types ---
from simulation.Component import Chassis, Component, ComponentSlot, ComputerProbe, PowerPack, SmallPowerPack
from simulation.DroidComponents import Motivator
from simulation.DroidAgents import DroidAgentSimple, DroidAgentSimplePowerDroid


class R2Astromech(Chassis):
    model:str = "R2 Astromech"
    sprite: str = "794.png"

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
    sprite: str = "Droid2 (1786).png"

    slots: Dict[str, ComponentSlot] = {
        "agent": ComponentSlot(accepts=DroidAgentSimple, component=DroidAgentSimplePowerDroid()),
        "power_pack": ComponentSlot(accepts=PowerPack, component=PowerPack()),
        "motivator": ComponentSlot(accepts=Motivator, component=Motivator()),
    }

