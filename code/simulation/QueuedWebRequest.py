
import threading
import requests
from typing import Any, Optional
from pydantic import BaseModel

class QueuedHttpRequest(BaseModel):
    url: str  # The URL to send the request to
    data: Optional[dict] = None  # The data to send in the request body
    in_progress: bool = False  # Whether the request is currently being sent
    response: Optional[Any] = None  # The response from the web request, if any
    _thread: Optional[threading.Thread] = None  # The thread that is running the web request
    headers: Optional[dict] = None  # Optional headers for the request

    def __init__(self, url: str, data: Optional[dict] = None, headers: Optional[dict] = {'Content-Type': 'application/json'}):
        super().__init__(url=url, data=data, headers=headers)

    def begin_send(self, timeout: Optional[float] = None):
        self.in_progress = True
        self.response = None
        self._thread = threading.Thread(target=self._send_request)
        self._thread.start()
        if timeout:
            timer = threading.Timer(timeout, self.cancel)
            timer.start()

    def _send_request(self):
        try:
            print(f"Sending request to {self.url} with data: {self.data}")
            resp = requests.post(self.url, json=self.data) #, headers=self.headers)
            resp.raise_for_status()
            self.response = resp.json()
            print(f"Received response: {self.response}")
        except Exception as e:
            self.response = {'error': str(e)}
            print(f"Request error: {e}")
        finally:
            self.in_progress = False

    def cancel(self):
        # Threads can't be forcefully killed in Python, so this is a no-op.
        self.in_progress = False
        print(f"Cancel called, but thread cannot be forcefully stopped in Python.")