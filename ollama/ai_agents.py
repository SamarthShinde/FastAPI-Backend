from typing import Dict, List, Optional
import requests
import json
import os
import sys
from datetime import datetime

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from api.config import OLLAMA_REMOTE_URL

# Available models dictionary
available_models = {
    "qwen2.5:3b": "qwen2.5:3b",   # default - upgrade OLLAMA for qwen3.5
    "llama3.2:3b": "llama3.2:3b",
    "gemma3": "gemma3",
}

class ChatAgent:
    """Agent for conversational interactions with Ollama models."""

    def __init__(self, model_name: str):
        if model_name not in available_models:
            raise ValueError(f"Unknown model: {model_name}. Available models are: {', '.join(available_models.keys())}")
        self.model_name = available_models[model_name]
        self.context = []
        self.system_prompt = """You are a helpful and knowledgeable AI assistant.
        Provide clear, accurate, and well-structured responses.
        If you're unsure about something, admit it."""
        self.conversation_history = []

    def _call_ollama(self, prompt: str, stream: bool = False):
        """Make API call to Ollama."""
        url = OLLAMA_REMOTE_URL
        headers = {"Content-Type": "application/json"}

        payload = {
            "model": self.model_name,
            "prompt": f"{self.system_prompt}\n\n{prompt}",
            "stream": False,
            "context": self.context
        }

        try:
            print(f"Calling Ollama API with model: {self.model_name}")
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            try:
                json_response = response.json()
                print(f"Ollama API response received")

                if "response" in json_response:
                    if "context" in json_response:
                        self.context = json_response["context"]
                    return json_response["response"]
                else:
                    error_msg = f"No 'response' field in Ollama API response: {json_response}"
                    print(error_msg)
                    return error_msg
            except json.JSONDecodeError as e:
                error_msg = f"Error decoding JSON from response: {str(e)}"
                print(error_msg)
                return error_msg

        except requests.exceptions.ConnectionError as e:
            error_msg = f"Failed to connect to Ollama API at {url}: {str(e)}"
            print(error_msg)
            return error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f"Error calling Ollama API: {str(e)}"
            print(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error in Ollama API call: {str(e)}"
            print(error_msg)
            return error_msg

    def chat(self, message: str, stream: bool = False, context_length: int = 5):
        """Handle chat interaction with context."""
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })

        # Build context from last N messages
        context_messages = []
        for msg in self.conversation_history[-context_length:]:
            role_prefix = "User: " if msg["role"] == "user" else "Assistant: "
            context_messages.append(f"{role_prefix}{msg['content']}")

        prompt = "\n".join(context_messages)
        if not prompt.endswith(message):
            prompt += f"\nUser: {message}"
        prompt += "\nAssistant:"

        try:
            response_content = self._call_ollama(prompt, stream=False)

            if response_content:
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response_content,
                    "timestamp": datetime.now().isoformat()
                })
                return response_content
            else:
                return "No response received from Ollama"
        except Exception as e:
            return f"Error in chat: {str(e)}"

class AgentFactory:
    """Factory class to create agents."""

    @staticmethod
    def create_agent(agent_type: str, model_name: str) -> ChatAgent:
        """Create an agent with the specified model."""
        return ChatAgent(model_name)
