import asyncio
import json
import os
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel
from simulation.core.World import World
from simulation.GlobalConfig import GlobalConfig

if TYPE_CHECKING:
    from simulation.core.entity.Chassis import \
        Chassis  # type: ignore

# --- Simulation System ---

# The Simulation is a high-level controller that manages the world and the simulation loop
class Simulation(BaseModel):
    running: bool = False  # Flag to control the simulation loop
    paused: bool = False  # Flag to pause the simulation
    tick_count: int = 0  # Number of ticks that have occurred in the simulation

    simulation_delay: float = 0.1  # Delay between simulation ticks in seconds
    simulation_delay_max: float = 0.5 # What is the maximum delay between simulation ticks? If LLM-based entities are thinking, then wait this long before proceeding to the next tick. This gives the simulation a semblance of determinism even as it runs at variable speeds.

    log_level: int = 0  # Log level for the simulation (0 = info, 1 = warning, 2 = error)

    # TODO: Make this more easily configurable -- possibly with a dictionary of endpoints for different model names or services.
    llm_url: str = "http://localhost:8080/v1/chat/completions"  # URL for the LLM endpoint

    world: World = World()  # The world that the simulation is running in

    _on_tick_subscribers: List = []  # List of callback functions to call after each tick

    # Singleton pattern to ensure only one instance of Simulation exists
    __instance: Optional['Simulation'] = None

    @classmethod
    def get_instance(cls, **data) -> 'Simulation':
        if not cls.__instance is None:
            return cls.__instance
        return cls(**data)
    
    def __init__(self, **data):
        super().__init__(**data)
        # Ensure the world is initialized
        if not self.world:
            self.world = World(**data.get('world', {}))
            
        Simulation.__instance = self  # Set the singleton instance

    def to_json(self):
        """Convert the simulation state to JSON format."""
        return {
            "running": self.running,
            "paused": self.paused,
            "llm_url": self.llm_url,
            "tick_count": self.tick_count,
            "simulation_delay": self.simulation_delay,
            "simulation_delay_max": self.simulation_delay_max,
            "log_level": self.log_level,
            "world": self.world.to_json(),
        }

    def run(self, ticks: Optional[int] = None):
        # Start the simulation loop in a separate thread
        simulation_task = asyncio.create_task(self._do_run(ticks))

        return simulation_task
    
    def run_sync(self, ticks: Optional[int] = None):
        """Run the simulation synchronously for a specified number of ticks."""

        # Run the simulation loop in a blocking manner
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError as e:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self._do_run(ticks))

    def subscribe_on_tick(self, callback):
        if callback not in self._on_tick_subscribers:
            self._on_tick_subscribers.append(callback)

    def unsubscribe_on_tick(self, callback):
        if callback in self._on_tick_subscribers:
            self._on_tick_subscribers.remove(callback)

    def dispatch_on_tick(self):
        """Call all on_tick subscribers."""
        for cb in self._on_tick_subscribers:
            try:
                cb(self)
            except Exception as e:
                print(f"[WARN] on_tick subscriber error: {e}")

    async def _do_run(self, ticks: Optional[int] = None):
        """Run the simulation asynchronously for a specified number of ticks."""
        self.running = True
        count = 0

        while self.running:
            sleep_time = 0.1

            if not self.paused:
                # Reset the thinking count at the start of each tick
                self.world.entity_thinking_count = 0

                # Advance the world by one tick
                self.world.tick()
                self.tick_count += 1
                count += 1
                # Call all on_tick subscribers
                for cb in self._on_tick_subscribers:
                    try:
                        cb(self)
                    except Exception as e:
                        print(f"[WARN] on_tick subscriber error: {e}")

                self.dispatch_on_tick()

                if GlobalConfig.simulation_dump_state:
                    state_full = self.to_json()
                    state_short = self.world.to_json(short=True)

                    os.makedirs("logs", exist_ok=True)
                    filename_full = f"sim_state_{Simulation.get_instance().tick_count}.json"
                    filename_short = f"world_state_{Simulation.get_instance().tick_count}.json"

                    short_state_changed = True

                    filename_short_prev = f"world_state_{Simulation.get_instance().tick_count - 1}.json"
                    # Check if the previous file exists
                    if os.path.exists(f"logs/{filename_short_prev}"):
                        # Check if it has the same contents as the current state
                        with open(f"logs/{filename_short_prev}", "r") as f:
                            state_short_prev = json.load(f)

                        if state_short_prev == state_short:
                            short_state_changed = False

                    # Only write the new state if it has changed
                    if short_state_changed:
                        with open(f"logs/{filename_full}", "w") as f:
                            try:
                                json.dump(state_full, f, indent=2)
                            except Exception as e:
                                # Write without dumping it as JSON -- just serialize as string
                                print(f"[WARN] Failed to write {filename_full}: {e}")
                                f.write(str(state_full))
                        with open(f"logs/{filename_short}", "w") as f:
                            json.dump(state_short, f, indent=2)
                    else:
                        print(f"Skipping world state dump for tick {Simulation.get_instance().tick_count} as it is unchanged from prev.")

                if ticks is not None and count >= ticks:
                    self.running = False
                    break

                sleep_time = self.simulation_delay

                # Check to see if any agents are thinking
                if self.world.entity_thinking_count > 0:
                    # If any entities are thinking, then give them the maximum delay to think
                    sleep_time = self.simulation_delay_max
                    print(f"Simulation: {self.world.entity_thinking_count} entities are thinking, sleeping for {sleep_time} seconds.")

            # Sleep for the specified delay before the next tick
            await asyncio.sleep(sleep_time)



# Resolve forward references now that World is fully defined.
from simulation.core.entity.Entity import Entity as _Entity

_Entity.model_rebuild()
