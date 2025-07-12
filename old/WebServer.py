import asyncio
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import StreamingResponse

app = FastAPI()
subscribers = set()

@app.get("/")
async def index():
    # Serve your Windows 3.1-style HTML/JS frontend here
    with open("simulation/web3point1-main/index.html") as f:
        return HTMLResponse(f.read())

@app.get("/events")
async def sse(request: Request):
    async def event_generator():
        queue = asyncio.Queue()
        subscribers.add(queue)
        try:
            while True:
                # If client disconnects, exit
                if await request.is_disconnected():
                    break
                data = await queue.get()
                yield f"data: {data}\n\n"
        finally:
            subscribers.remove(queue)
    return StreamingResponse(event_generator(), media_type="text/event-stream")

def broadcast_game_state(game_state: dict):
    data = json.dumps(game_state)
    for queue in list(subscribers):
        queue.put_nowait(data)