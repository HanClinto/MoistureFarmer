# A PowerGenerator is a component that can automatically recharge adjacent power packs.
from simulation.core.entity.component.PowerPack import PowerPack
from simulation.core.entity.component.Component import Component

class PowerGenerator(Component):
    cooldown_remaining: int = 0  # Cooldown for action after each tick
    cooldown_delay:     int = 8  # Cooldown delay in ticks
    recharge_amount:    int = 1  # Amount of charge to add per cycle

    @property
    def current_cooldown(self) -> int:
        return self.cooldown_remaining

    @current_cooldown.setter
    def current_cooldown(self, v: int):
        self.cooldown_remaining = max(0, v)

    # TODO: Bring CooldownComponent into its own class, and make use of it here and in Motivator

    def tick(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
            return False

        # Recharge other power packs in this same entity
        power_pack: PowerPack = self.chassis.get_component(PowerPack)
        if power_pack:
            power_pack.charge += self.recharge_amount
            power_pack.charge = min(power_pack.charge, power_pack.charge_max)

        self.current_cooldown = self.cooldown_delay
        return
