import threading 
import asyncio
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from simulation.World import Simulation

app = FastAPI()
subscribers = set()

# Serve static files (web assets and sprites)
web31_root = Path(__file__).parent / 'web31'
web98_root = Path(__file__).parent / 'web98'
app.mount('/web98', StaticFiles(directory=web98_root), name='web98')
app.mount('/web31', StaticFiles(directory=web31_root), name='web31')

# Redirect root to the /web98 directory
@app.get("/")
async def redirect_root():
    return HTMLResponse(status_code=302, headers={"Location": "/web98/index.html"})

@app.get("/events")
async def sse(request: Request):
    print(f'*** New SSE connection from {request.client.host} ***')
    async def event_generator():
        queue = asyncio.Queue()
        subscribers.add(queue)
        try:
            while True:
                if await request.is_disconnected():
                    break
                data = await queue.get()
                yield f"data: {data}\n\n"
        finally:
            subscribers.remove(queue)
    
    # Firefox-compatible headers for SSE
    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Headers": "Cache-Control",
    }
    
    return StreamingResponse(
        event_generator(), 
        media_type="text/event-stream",
        headers=headers
    )

def broadcast_simulation_state(simulation: Simulation):
    sim_state = json.dumps(simulation.to_json())
    for queue in list(subscribers):
        queue.put_nowait(sim_state)

# --- Simulation integration ---
simulation:Simulation = None
simulation_thread:threading.Thread = None

def initialize_simulation() -> tuple[Simulation, threading.Thread]:
    simulation = Simulation()
    simulation.simulation_delay = 5.0  # Set a default simulation delay
    simulation.simulation_delay_max = 10.0  # Set a maximum simulation delay

    attach_to_simulation(simulation)

    thread = threading.Thread(target=simulation.run_sync, args=(None,))
    thread.start()

    return simulation, thread

def attach_to_simulation(sim: Simulation):
    def on_tick(simulation):
        broadcast_simulation_state(simulation)
    sim.subscribe_on_tick(on_tick)

@app.on_event("startup")
async def startup_event():
    global simulation, simulation_thread
    simulation, simulation_thread = initialize_simulation()

@app.on_event("shutdown")
async def shutdown_event():
    global simulation, simulation_thread
    if simulation:
        simulation.running = False
        simulation_thread.join()
        simulation = None
        simulation_thread = None