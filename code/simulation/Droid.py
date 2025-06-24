from typing import ClassVar, Dict, Optional, List, Type, Optional
from pydantic import BaseModel
from simulation.World import World
from simulation.Entity import Location
from simulation.Component import Chassis, ComponentSlot, Component, PowerPack, SmallPowerPack, ComputerProbe

# --- Droid Components ---
class Motivator(Component):
    def provides(self):
        return ["move_to_location", "move_to_object"]

    def on_tick(self, world: World):
        if self.chassis.destination == self.chassis.location:
            # If the destination is the same as the current location, do nothing
            return

        power = self.chassis.get_component(PowerPack)
        if not power:
            print("No power pack found in the chassis. CondenserUnit cannot function without a power pack.")
            # TODO: Post an error message that the AI can see
            return

        if power.charge <= 0:
            print("Power pack is empty. Cannot move without power!")
            # TODO: Post an error message to world and/or chassis system?
            return

        # TODO: Collision checking vs. the world map

        curr = self.chassis.location
        dest = self.chassis.destination
        dx = dest.x - curr.x
        dy = dest.y - curr.y
        if dx != 0:
            curr.x += 1 if dx > 0 else -1
            power.charge -= 1  # Consume power for movement
        elif dy != 0:
            curr.y += 1 if dy > 0 else -1
            power.charge -= 1  # Consume power for movement
        else:
            self.chassis.destination = None



class AStarMotivator(Motivator):
    def provides(self):
        return super().provides() + ["find_path"]

    def find_path(self, world: World, start: Location, end: Location) -> List[Location]:
        # Placeholder for A* pathfinding logic
        path = []
        curr = start
        while curr != end:
            if curr.x < end.x:
                curr = Location(x=curr.x + 1, y=curr.y)
            elif curr.x > end.x:
                curr = Location(x=curr.x - 1, y=curr.y)
            elif curr.y < end.y:
                curr = Location(x=curr.x, y=curr.y + 1)
            elif curr.y > end.y:
                curr = Location(x=curr.x, y=curr.y - 1)
            path.append(curr)
        return path

    def on_tick(self, world: World):
        # Use A* pathfinding to move towards the destination
        # TODO: Implement collision checking vs. the world map
        # TODO: Implement A*
        if self.chassis and self.chassis.destination:
            # TODO: Cache the path as long as the destination has not changed
            path = self.find_path(world, self.chassis.location, self.chassis.destination)
            if path:
                next_location = path[0]
                self.chassis.location = next_location
                if next_location == self.chassis.destination:
                    self.chassis.destination = None


# --- Specific Droid Types ---
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
        "power_pack": ComponentSlot(accepts=PowerPack, component=PowerPack()),
        "motivator": ComponentSlot(accepts=Motivator, component=Motivator()),
    }

