
from simulation.core.entity.component.PowerGenerator import PowerGenerator


class SolarPanel(PowerGenerator):
    cooldown_delay: int  = 10   # Cooldown delay in ticks
    recharge_amount: int = 10   # Amount of charge to add per cycle
    description: str = "An I-a2b solar ionization panel that has been scavenged from a long-abandoned wreck and repurposed to harness energy production amidst the endless sands of Tatooine. It was originally a power system designed by Sienar Fleet Systems, but it is a long way from the original form it used to have. It still has enough of its girondium-colium core to function, albeit at a reduced efficiency."

class MicroFusionPowerCell(PowerGenerator):
    cooldown_delay: int  = 2   # Cooldown delay in ticks
    recharge_amount: int = 50   # Amount of charge to add per cycle
    description: str = "A micro nuclear power cell that uses advanced fusion technology to generate energy."
