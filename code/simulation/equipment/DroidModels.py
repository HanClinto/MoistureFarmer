from typing import Dict

# --- Specific Droid Types ---
from simulation.core.entity.Chassis import Chassis
from simulation.core.entity.component.Component import Component
from simulation.core.entity.ComponentSlot import ComponentSlot
from simulation.core.entity.component.ComputerProbe import ComputerProbe
from simulation.core.entity.component.Motivator import Motivator
from simulation.core.entity.component.PowerAdapter import HeavyDutyPowerAdapter, PowerAdapter
from simulation.core.entity.component.PowerPack import (PowerPack,
                                                        SmallPowerPack)
from simulation.equipment.DroidAgentModels import (DroidAgentSimple,
                                                   DroidAgentSimplePowerDroid)

Chassis.model_rebuild()
ComponentSlot.model_rebuild()
PowerPack.model_rebuild()
SmallPowerPack.model_rebuild()
ComputerProbe.model_rebuild()

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
        "power_adapter": ComponentSlot(accepts=PowerAdapter, default_component=PowerAdapter),
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
        "power_adapter": ComponentSlot(accepts=PowerAdapter, default_component=HeavyDutyPowerAdapter),
        "misc": ComponentSlot(accepts=Component),  # For any additional components
    }
    
    def __init__(self, **data):
        super().__init__(**data)
        # Install default agent component after initialization
        if not self.slots["agent"].component:
            self.install_component("agent", DroidAgentSimplePowerDroid())

# Star Wars Trilogy Sourcebook: WEG40089.pdf
# Power droids are so common throughout the galaxy and their design and features so standardized that they aren't even given code letters by the general populace (although they do still have identifying numbers). Power droids serve as mobile battery packs and capacitors, storing energy to distribute to other droids and machinery. These droids are almost exclusively used in rural areas where power grids
# aren't available, newly established colonies where power generating plants haven't been constructed yet, and as back-
# up systems for small private dwellings, ships or businesses. Most power droids have very little in the way of logic
# circuits: just enough to obey simple voice commands and operate the stumpy little legs so characteristic of the box- like machines. Some, however, have been modified either by tinkering owners or at the request of task-specific custom- ers. Power droids have little need for inherent thought programming, and as a result such units have been known to jump off a landing platform without argument if told to do so (which has become a common juvenile prank on many worlds).
# The power droid aboard the Jawa sandcrawler, which became involved with R2-D2 and C-3PO, is a special case. This particular power droid had been slightly modified with enhanced intelligence modules. Because of this modifica- tion, it can serve a dual role as a diagnostics systems analyzer. It is particularly adept at dealing with farm and agricultural equipment, having spent most of its existence on a Tatooine moisture farm.
# Prior to the start of the events that culminated with the battle of Yavin, this farm was raided by Sand People, its owners killed. Scavenging Jawas recovered the droid and some remaining equipment abandoned by the Tusken Raid- ers.lt was placed in the same cargo bay that would later hold RS-D4, R2-D2 and C-3PO.
# This particular mechanical is very friendly and can actually give advice about how to correct certain technical problems. Since the droid's identification numbers were removed and it claims to have no memory of when this was done, it does not have a name to call its own. This fact doesn't bother the spunky droid, however, and it is content to know that it is a step above its immediate peers.
