from typing import Any, Callable, Dict, Optional, List, Type
from simulation.llm.ToolCall import ToolCallResult, ToolCallState, tool
from simulation.core.World import World
from simulation.core.Simulation import Simulation
from simulation.core.entity.Entity import Location
from simulation.core.entity.component.Component import Chassis, ComponentSlot, Component, PowerPack
from random import randint
from simulation.movement_intent import MovementIntent
import logging

# Chronometer is a component that allows droids to be aware of time.
# For now, it only provides a single tool call to allow sleeping for a specified number of ticks.
class Chronometer(Component):
    name: str = "Chronometer"

    wake_time: int = 0 # The tick at which the droid will wake up

    @tool
    def sleep(self, ticks: int) -> ToolCallResult:
        """
        Sleep for a specified number of ticks.
        Args:
            ticks (int): The number of ticks to sleep.
        """
        if ticks <= 0:
            raise ValueError("Ticks must be a positive integer.")
        self.info(f"Sleeping for {ticks} ticks.")
        self.wake_time = Simulation.get_instance().tick_count + ticks
        self.info(f"Will wake up at tick {self.wake_time}.")

        return ToolCallResult(
            state=ToolCallState.IN_PROCESS,
            callback=self.sleep_isdone
        )

    def sleep_isdone(self) -> ToolCallResult:
        """
        Check if the sleep is done.
        Returns:
            ToolCallResult: The result of the tool call.
        """
        if Simulation.get_instance().tick_count >= self.wake_time:
            return ToolCallResult(state=ToolCallState.SUCCESS, message=f"Woke up from sleep at {self.wake_time} ticks.")
        return ToolCallResult(state=ToolCallState.IN_PROCESS)

Chronometer.model_rebuild()
