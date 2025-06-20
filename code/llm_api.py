import requests

class LlmApi:
    def __init__(self, endpoint="http://localhost:8080/v1/chat/completions"):
        self.endpoint = endpoint

    def get_completion(self, messages, tools):
        query = {
            "model": "gpt-4-turbo",
            "tools": tools,
            "tool_choice": "auto",
            "messages": messages,
            "temperature": 0.2
        }
        response = requests.post(self.endpoint, json=query)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
