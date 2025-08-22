from simulation.core.entity.component.WaterTank import WaterTank


class SmallWaterTank(WaterTank):
    capacity: int = 50

class LargeWaterTank(WaterTank):
    capacity: int = 200
