from simulation.core.entity.component.Component import Component


class WaterTank(Component):
    fill: int = 0
    capacity: int = 100

class SmallWaterTank(WaterTank):
    capacity: int = 50

class LargeWaterTank(WaterTank):
    capacity: int = 200
