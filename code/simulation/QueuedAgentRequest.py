
import asyncio
import aiohttp
from typing import Optional
from pydantic import BaseModel
from llama_cpp_agent import LlamaCppAgent

class QueuedAgentRequest(BaseModel):
    in_progress: bool = False  # Whether the request is currently being sent
    response: Optional[str] = None  # The response from the web request, if any
    _task: Optional[asyncio.Task] = None  # The task that is running the web request

    def __init__(self, url: str, data: Optional[dict] = None):
        self.url = url
        self.data = data

    def begin_send(self, timeout: Optional[float] = None):
        # Send the request to the URL.
        # When it's done, set in_progress to False and response to the response from the web request.
        self.in_progress = True
        self.response = None  # Reset response before sending

        # Check to see if there is an event loop running
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError as e:
            if 'There is no current event loop in thread' in str(e):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            else:
                raise e

        # Create an asyncio task to send the request, with optional timeout
        if timeout:
            self._task = asyncio.create_task(self._send_request_async())
            self._task.add_done_callback(lambda t: asyncio.get_event_loop().call_later(timeout, self.cancel))
        else:
            self._task = asyncio.create_task(self._send_request_async())

    async def _send_request_async(self):
        # Send the request asynchronously
        print(f"Sending request to {self.url} with data: {self.data}")
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=self.data) as response:
                self.response = await response.text()
                self.in_progress = False
                print(f"Received response: {self.response}")

    def cancel(self):
        # Cancel the request if it is in progress
        if self._task and not self._task.done():
            self._task.cancel()
            self.in_progress = False
            print(f"Request to {self.url} has been cancelled.")
        else:
            print(f"No active request to cancel for {self.url}.")