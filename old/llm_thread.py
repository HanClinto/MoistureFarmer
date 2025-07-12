import requests
import json

class LlmThread:
    def __init__(self, system_prompt, sample_conversations, gonky, endpoint="http://localhost:8080/v1/chat/completions"):
        self.endpoint = endpoint
        self.messages = []
        self._initialize_messages(system_prompt, sample_conversations, gonky)

    def _fill_vars(self, prompt, obj):
        """Fill in the variables in the prompt with the values from the object."""
        return prompt.format(**obj)

    def _initialize_messages(self, system_prompt, sample_conversations, gonky):
        self.messages.append({"role": "system", "content": self._fill_vars(system_prompt, gonky)})
        for conversation in sample_conversations:
            self.messages.append({"role": "user", "content": conversation["user"]})
            self.messages.append({"role": "assistant", "content": self._fill_vars(conversation["assistant"], gonky)})

    def add_tool_response(self, tool_response_message):
        self.messages.append(tool_response_message)

    def get_completion(self, daily_prompt, farm_status, tools):
        # Add user message for this turn
        user_message = {"role": "user", "content": self._fill_vars(daily_prompt, {"farm_status": json.dumps(farm_status)})}
        self.messages.append(user_message)

        query = {
            "model": "gpt-4-turbo",
            "tools": tools,
            "tool_choice": "auto",
            "messages": self.messages,
            "temperature": 0.2
        }
        response = requests.post(self.endpoint, json=query)
        response.raise_for_status()  # Raise an exception for bad status codes
        response_json = response.json()
        
        # Append the assistant's message to the history
        if response_json["choices"]:
            assistant_message = response_json["choices"][0]["message"]
            self.messages.append(assistant_message)
            
        return response_json
