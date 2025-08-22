from simulation.core.entity.component.Component import Component

# --- Specific Component Systems ---
class PowerPack(Component):
    charge_max: int = 100
    charge: int = 100

class SmallPowerPack(PowerPack):
    charge_max: int = 50
    charge: int = 50

class LargePowerPack(PowerPack):
    charge_max: int = 200
    charge: int = 200
