from typing import Callable, Optional
from simulation.core.Simulation import World
from simulation.core.entity.Chassis import Chassis
from simulation.core.entity.component.PowerPack import PowerPack
from simulation.core.entity.component.Component import Component
from simulation.llm.ToolCall import ToolCallResult, ToolCallState, tool


class PowerConverter(Component):
    model: str = "Universal Power Converter"
    description: str = "A universal power converter that allows a unit to recharge itself from any adjacent power source."

    transfer_rate: int = 2  # Amount of charge to transfer per tick

    transfer_target_id: Optional[str] = None  # The entity to transfer charge between us and them
    transfer_mode: Optional[str] = None  # The mode of transfer (e.g. "Charge" or "Recharge")

    tool_result: ToolCallResult = None

    # The Udrane Galactic Electronics Universal Power Adaptor enables a droid to connect to another entity to deposit or withdraw charge from its power banks.
    #  While the term "universal" may be a hyperbolic piece of marketing fluff, neveretheless, Udrane Galactic Electronics managed to create a reliable piece of technology that is the backbone of modern energy transfer systems.

    @tool
    def recharge_self(self, identifier: str) -> Callable[..., ToolCallResult]:
        """
        Recharge our power pack from an adjacent entity.
        Args:
            identifier (str): The ID of the entity to recharge from. Must be adjacent.
        """
        # TODO: If the identifier is none, should we recharge from the nearest power station?
        #  Or maybe just whatever is nearest to us (power station or not)?
        return self.begin_transfer(identifier, "Recharge")

    def begin_transfer(self, identifier:str, mode:str) -> Callable[..., ToolCallResult]:
        world: World = self.chassis.world

        # Find the entity by ID and set the destination to its location
        entities = world.get_entities(identifier)

        if len(entities) == 0:
            msg = f"{mode} failed. No entity found with identifier `{identifier}`."
            self.error(msg)
            return ToolCallResult(state=ToolCallState.FAILURE, message=msg)

        # Sort entities by distance to the chassis
        entities.sort(key=lambda e: self.chassis.location.distance_to(e.location))
        entity = entities[0]  # Get the closest entity

        # Check if the entity is adjacent
        distance = self.chassis.location.distance_to(entity.location)
        if not distance < 2:
            msg = f"{mode} failed. `{identifier}` is {distance} units away. Must be adjacent."
            self.error(msg)
            return ToolCallResult(state=ToolCallState.FAILURE, message=msg)

        self.tool_result = ToolCallResult(state=ToolCallState.IN_PROCESS, callback=self.charge_transfer_isdone)
        self.transfer_target_id = entity.id
        self.transfer_mode = mode

        return self.tool_result

    def tick(self):
        if not self.transfer_target_id:
            # Nothing to do, so just return.
            return

        them: Chassis = self.chassis.world.get_entity(self.transfer_target_id)
        mode = self.transfer_mode

        if not them:
            msg = f"{mode} failed. No entity found with ID `{self.transfer_target_id}`."
            self.error(msg)
            self.tool_result = ToolCallResult(state=ToolCallState.FAILURE, message=msg)
            self.transfer_target_id = None
            # Nothing to do, so just return.
            return

        # Ensure that we are adjacent to our other entity
        distance = self.chassis.location.distance_to(them.location)
        if not distance < 2:
            # Report an error and fail the charge. We are no longer adjacent.
            msg = f"{mode} failed. No longer adjacent to {them.id}. {them.id} is {distance} units away."
            self.error(msg)
            self.tool_result = ToolCallResult(state=ToolCallState.FAILURE, message=msg)
            self.transfer_target_id = None
            return

        # Ensure that we have power in the other source's PowerPack
        their_powerpack = them.get_component(PowerPack)
        if not their_powerpack:
            msg = f"{mode} failed. {them.id} does not have a PowerPack."
            self.error(msg)
            self.tool_result = ToolCallResult(state=ToolCallState.FAILURE, message=msg)
            self.transfer_target_id = None
            return

        our_powerpack = self.chassis.get_component(PowerPack)
        if not our_powerpack:
            msg = f"{mode} failed. We ({self.chassis.id}) do not have a PowerPack."
            self.error(msg)
            self.tool_result = ToolCallResult(state=ToolCallState.FAILURE, message=msg)
            self.transfer_target_id = None
            return

        charge_source = their_powerpack if mode == "Recharge" else our_powerpack
        charge_target = our_powerpack if mode == "Recharge" else their_powerpack

        needed_charge = charge_target.charge_max - charge_target.charge
        supply_charge = charge_source.charge

        if needed_charge > 0 and supply_charge < self.transfer_rate:
            # Warn if the other powerpack is low on charge, but do not fail.
            self.warn(f"{charge_source.chassis.id} is low on power ({charge_source.charge}/{charge_source.charge_max}).")

        charge_amount = min(needed_charge, supply_charge, self.transfer_rate)

        # Apply the transfer
        charge_source.charge -= charge_amount
        charge_target.charge += charge_amount

        if charge_target.charge == charge_target.charge_max:
            msg = f"{mode} complete: {charge_target.chassis.id} power at {charge_target.charge}/{charge_target.charge_max}"
            self.tool_result = ToolCallResult(state=ToolCallState.SUCCESS, message=msg)
            self.transfer_target_id = None
        else:
            msg = f"{mode} in progress: Transferred {charge_amount} units from {charge_source.chassis.id}. {charge_target.chassis.id} power at {charge_target.charge}/{charge_target.charge_max}"
            self.tool_result = ToolCallResult(state=ToolCallState.IN_PROCESS, callback=self.charge_transfer_isdone, message=msg)
            self.info(msg)

    def charge_transfer_isdone(self) -> None:
        return self.tool_result


class HeavyDutyPowerConverter(PowerConverter):
    model: str = "Heavy-Duty Universal Power Converter"
    description: str = "A heavy-duty power converter designed for high-capacity power transfer. Can recharge other equipment, in addition to itself."

    transfer_rate: int = 5  # Amount of charge to transfer per tick

    @tool
    def charge_other(self, identifier: str) -> Callable[..., ToolCallResult]:
        """
        Charge an adjacent entity from this unit's power pack.
        Args:
            identifier (str): The ID of the entity to charge. Must be adjacent.
        """
        # TODO: If the identifier is none, should we recharge whatever is nearby to us?
        return self.begin_transfer(identifier, "Charge")
