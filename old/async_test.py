# Spawn a bunch of objects that all have an async tick() method.
# Call their tick() method concurrently and wait for all of them to finish.
# This is a test to ensure that the async tick() method works correctly.

import asyncio
from typing import List, Optional
from pydantic import BaseModel
from random import randint

class AsyncEntity(BaseModel):
    id: str
    name: str
    delay: int = randint(1, 5)
    async def tick(self) -> None:
        # Simulate some asynchronous work
        # Simulate sleeping between 0.1 and 0.5 seconds
        print(f"Entity {self.name} with ID {self.id} is ticking with delay {self.delay * 0.1} seconds...")
        await asyncio.sleep(self.delay * 0.1)
        print(f"Entity {self.name} with ID {self.id} ticked.")

class AsyncEntityLongDelay(AsyncEntity):
    delay: int = 25  # Override to have a longer delay for testing

class Simulation(BaseModel):
    entities: List[AsyncEntity] = []

    def add_entity(self, entity: AsyncEntity) -> None:
        self.entities.append(entity)

    async def run(self, num_ticks) -> None:
        print("Starting simulation...")
        for tick in range(num_ticks):
            print(f" Tick {tick + 1}/{num_ticks}")
            await self.tick()
            # Wait 1 seconds between ticks
            await asyncio.sleep(1)
        print("Simulation finished.")

    async def tick(self) -> None:
        await asyncio.gather(*(entity.tick() for entity in self.entities))

async def main():
    simulation = Simulation()

    # Create and add some entities
    for i in range(5):
        entity = AsyncEntity(id=f"entity_{i}", name=f"Entity {i}")
        simulation.add_entity(entity)

    # Add an entity with a longer delay for testing
    long_delay_entity = AsyncEntityLongDelay(id="long_delay_entity", name="Long Delay Entity")
    simulation.add_entity(long_delay_entity)

    # Run the simulation
    await simulation.run(num_ticks=30)

if __name__ == "__main__":
    asyncio.run(main())
