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

# Redirect root to the /web31 directory
@app.get("/")
async def redirect_root():
    return HTMLResponse(status_code=302, headers={"Location": "/web98/index.html"})

@app.get("/events")
async def sse(request: Request):
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
    return StreamingResponse(event_generator(), media_type="text/event-stream")

def broadcast_game_state(simulation: Simulation):
    game_state = json.dumps(simulation.world.to_json())
    for queue in list(subscribers):
        queue.put_nowait(game_state)

# --- Simulation integration ---
def attach_to_simulation(sim: Simulation):
    def on_tick(simulation):
        broadcast_game_state(simulation)
    sim.subscribe_on_tick(on_tick)
