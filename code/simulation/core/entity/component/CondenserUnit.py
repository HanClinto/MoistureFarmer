from simulation.core.entity.component.Chassis import Component
from simulation.core.entity.component.PowerPack import PowerPack
from simulation.core.entity.component.WaterTank import WaterTank

# --- Supporting Components for Vaporators ---

class CondenserUnit(Component):
    water_per_charge: int = 1 # Amount of water condensed per unit of charge

    def tick(self):
        # self.info(f"Tick: {self.water_per_charge} water per charge")

        if not self.chassis:
            raise ValueError("CondenserUnit must be installed in a chassis to function.")
        
        tank = self.chassis.get_component(WaterTank)
        if not tank:
            self.error("No water tank found in the chassis. CondenserUnit cannot function without a water tank.")
            # TODO: Post an error message that the AI can see
            return

        power = self.chassis.get_component(PowerPack)
        if not power:
            self.error("No power pack found in the chassis. CondenserUnit cannot function without a power pack.")
            # TODO: Post an error message that the AI can see
            return

        if tank.fill >= tank.capacity:
            #self.warn("Water tank is full. CondenserUnit cannot condense more water.")
            # TODO: Post an error message to world and/or chassis system?
            return
        if power.charge <= 0:
            #self.warn("Power pack is empty. CondenserUnit cannot condense water.")
            # TODO: Post an error message to world and/or chassis system?
            return
            
        # Condense water
        # TODO: Condense less water if the Condensor is in poor condition
        # TODO: Condense more water if the Condensor has been tuned / adjusted recently
        power.charge -= 1
        tank.fill += self.water_per_charge

class AdvancedCondenserUnit(CondenserUnit):
    water_per_charge: int = 2 # More efficient condenser, condenses more water per unit of charge
