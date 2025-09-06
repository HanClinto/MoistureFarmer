from simulation.core.entity.component.Component import Component

# --- Specific Component Systems ---
class PowerPack(Component):
    charge_max: int = 1000
    charge: int = 1000

class SmallPowerPack(PowerPack):
    charge_max: int = 500
    charge: int = 500

class LargePowerPack(PowerPack):
    # Dylinium hydride power pack
    charge_max: int = 2000
    charge: int = 2000
