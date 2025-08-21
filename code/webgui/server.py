import threading 
import asyncio
import json
import os
from simulation.AutoScenarioManager import AutoScenarioManager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from simulation.core.entity.component.DroidAgents import DroidAgent
from simulation.core.World import Simulation
from simulation.core.entity.RandomWalker import RandomWalker  # NEW

app = FastAPI()
subscribers = set()
movement_subscribers = set()

# Serve static files (web assets and sprites)
web31_root = Path(__file__).parent / 'web31'
web98_root = Path(__file__).parent / 'web98'
app.mount('/web98', StaticFiles(directory=web98_root), name='web98')

resources_root = Path(__file__).parent / 'resources'
app.mount('/resources', StaticFiles(directory=resources_root), name='resources')

# Redirect root to the /web98 directory
@app.get("/")
async def redirect_root():
    return HTMLResponse(status_code=302, headers={"Location": "/web98/index.html"})

def _generic_sse_endpoint(subscriber_set, request: Request):
    async def event_generator():
        queue = asyncio.Queue()
        subscriber_set.add(queue)
        try:
            while True:
                if await request.is_disconnected():
                    break
                event = await queue.get()  # Expect already formatted string with event & data lines
                yield event
        finally:
            subscriber_set.remove(queue)
    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Headers": "Cache-Control",
    }
    return StreamingResponse(event_generator(), media_type="text/event-stream", headers=headers)

@app.get("/events")
async def sse(request: Request):
    # Legacy combined stream of full simulation state each tick (no explicit event name)
    print(f'*** New SSE (state) connection from {request.client.host} ***')
    return _generic_sse_endpoint(subscribers, request)

@app.get("/movement_events")
async def movement_sse(request: Request):
    print(f'*** New SSE (movement) connection from {request.client.host} ***')
    return _generic_sse_endpoint(movement_subscribers, request)

@app.post("/simulation/simulation_delay/{simulation_delay}")
def set_simulation_delay(simulation_delay: float):
    # Cannot set simulation delay above simulation_delay_max
    simulation_delay = min(simulation_delay, simulation.simulation_delay_max)
    simulation.simulation_delay = simulation_delay
    return {"status": "success"}

@app.post("/simulation/paused/{paused_bool}")
def set_simulation_paused(paused_bool: bool):
    if simulation:
        simulation.paused = paused_bool
        return {"status": "success"}
    return {"error": "No simulation loaded"}

@app.get("/simulation")
def get_simulation_state():
    """Get the current state of the simulation."""
    if simulation:
        return simulation.to_json()
    else:
        return {"error": "No simulation loaded"}

# --- Scenario Save/Load Endpoints ---
@app.post("/scenario/save")
async def save_scenario(request: Request):
    """Serialize the current simulation and return as JSON file."""
    if not simulation:
        return {"error": "No simulation loaded"}
    body = await request.json()
    name = body.get("name", "Scenario")
    description = body.get("description", "")
    scenario_data = AutoScenarioManager._simulation_to_dict(simulation, name, description)
    return HTMLResponse(
        content=json.dumps(scenario_data, indent=2),
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename={name}.json"
        }
    )

@app.post("/scenario/load")
async def load_scenario(request: Request):
    """Load a scenario from uploaded JSON and replace the global simulation."""
    try:
        scenario_data = await request.json()
        print(f'*** Loading scenario with data: {scenario_data} ***')

        # Use AutoScenarioManager to create a new Simulation
        AutoScenarioManager._dict_to_simulation(scenario_data)
        
        print("Scenario loaded successfully")

        # Immediately broadcast the new simulation state
        broadcast_simulation_state(simulation)

        return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}
    
@app.post("/droid/chat/{droid_id}")
async def droid_chat(droid_id: str, request: Request):
    """Handle chat messages for a specific droid."""
    if not simulation:
        return {"error": "No simulation loaded"}
    body = await request.json()
    message = body.get("message", "")
    print(f'*** Droid {droid_id} sent message: {message} ***')
    # Here you would add logic to process the droid's message
    droid = simulation.world.get_entity(droid_id)
    if not droid:
        return {"error": f"Droid with ID {droid_id} not found"}
    
    # Get the agent component of the droid
    agent = droid.get_component(DroidAgent)

    if not agent:
        return {"error": f"Droid {droid_id} does not have an agent component"}
    
    # If the agent is already active and processing, for now we will just return an error
    if agent.is_active:
        return {"error": f"Droid {droid_id} is already processing a request"}
    
    # Activate the agent with the message
    agent.activate(message)

    # Immediately broadcast the updated simulation so clients can reflect busy state
    broadcast_simulation_state(simulation)

    return {"status": "success", "message": f"Droid {droid_id} is processing the message: {str(agent.last_message())}"}

def broadcast_simulation_state(simulation: Simulation):
    sim_state = json.dumps(simulation.to_json(), ensure_ascii=False, default=str)
    # Format per SSE spec (data: lines + blank line). We leave event name blank for legacy endpoint.
    payload = f"data: {sim_state}\n\n"
    for queue in list(subscribers):
        queue.put_nowait(payload)

def broadcast_movement_journal(simulation: Simulation):
    if not simulation.world.last_movement_journal:
        return
    movement_payload = json.dumps({
        "tick": simulation.tick_count,
        "movements": simulation.world.last_movement_journal,
    })
    event_block = f"event: movements\ndata: {movement_payload}\n\n"
    for queue in list(movement_subscribers):
        queue.put_nowait(event_block)

# --- Simulation integration ---
simulation:Simulation = None
simulation_thread:threading.Thread = None

def initialize_simulation() -> tuple[Simulation, threading.Thread]:
    simulation = Simulation()
    simulation.simulation_delay = 2.0  # Set a default simulation delay
    simulation.simulation_delay_max = 10.0  # Set a maximum simulation delay

    # Spawn a few random walkers if tilemap available (will lazy init on first tick otherwise)
    world = simulation.world
    if world.tilemap is None:
        world.tilemap = world.tilemap or None  # will be created in first tick; we can still place walkers at default interior
    # Place walkers near center after tilemap init in first tick; so subscribe a one-shot to add them once tilemap exists
    from simulation.core.entity.Entity import Location
    def add_walkers_once(sim):
        """One-shot callback to add initial random walkers once the tilemap exists."""
        if sim.world.tilemap is None:
            return  # wait until tilemap created on first tick
        tm = sim.world.tilemap
        cx, cy = tm.width // 2, tm.height // 2
        # Spawn a handful of walkers near center (spread diagonally for now)
        for i in range(25):
            walker = RandomWalker(id=f"walker_{i}", location=Location(x=cx + i, y=cy + i))
            sim.world.add_entity(walker)
        # Unsubscribe so this only happens once
        sim.unsubscribe_on_tick(add_walkers_once)
    simulation.subscribe_on_tick(add_walkers_once)

    attach_to_simulation(simulation)

    thread = threading.Thread(target=simulation.run_sync, args=(None,))
    thread.start()

    return simulation, thread

def attach_to_simulation(sim: Simulation):
    def on_tick(simulation):
        broadcast_simulation_state(simulation)
        broadcast_movement_journal(simulation)
    sim.subscribe_on_tick(on_tick)

@app.on_event("startup")
async def startup_event():
    global simulation, simulation_thread
    simulation, simulation_thread = initialize_simulation()

    # Optionally load a default scenario from environment variable
    scenario_path = os.environ.get("MF_DEFAULT_SCENARIO")
    if scenario_path:
        try:
            AutoScenarioManager.load_simulation_from_json(scenario_path)
            broadcast_simulation_state(simulation)
            print(f"[INFO] Loaded default scenario: {scenario_path}")
        except Exception as e:
            print(f"[WARN] Failed to load default scenario '{scenario_path}': {e}")

@app.on_event("shutdown")
async def shutdown_event():
    global simulation, simulation_thread
    if simulation:
        simulation.running = False
        simulation_thread.join()
        simulation = None
        simulation_thread = None