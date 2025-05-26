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

from backend.config import OLLAMA_REMOTE_URL

# Available models dictionary
available_models = {
    "llama3.2:3b": "llama3.2:3b",  # 2.0 GB
    "gemma3": "gemma3"             # 3.3 GB
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
        
        # Always set stream to False in the payload for simplicity
        payload = {
            "model": self.model_name,
            "prompt": f"{self.system_prompt}\n\n{prompt}",
            "stream": False,
            "context": self.context
        }
        
        try:
            print(f"Calling Ollama API with model: {self.model_name}")
            # Make the API call
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            # Parse the response
            try:
                json_response = response.json()
                print(f"Ollama API response: {json_response}")
                
                if "response" in json_response:
                    # Save context for future calls
                    if "context" in json_response:
                        self.context = json_response["context"]
                    
                    # Return the response text
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
        # Add message to history
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Build context from last N messages based on subscription
        context_messages = []
        for msg in self.conversation_history[-context_length:]:
            role_prefix = "User: " if msg["role"] == "user" else "Assistant: "
            context_messages.append(f"{role_prefix}{msg['content']}")
        
        # Prepare prompt with context
        prompt = "\n".join(context_messages)
        if not prompt.endswith(message):
            prompt += f"\nUser: {message}"
        prompt += "\nAssistant:"
        
        try:
            # Get response from Ollama
            response_content = self._call_ollama(prompt, stream=False)
            
            if response_content:
                # Add response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response_content,
                    "timestamp": datetime.now().isoformat()
                })
                
                return response_content
            else:
                error_msg = "No response received from Ollama"
                return error_msg
        except Exception as e:
            error_msg = f"Error in chat: {str(e)}"
            return error_msg

class AgentFactory:
    """Factory class to create agents."""
    
    @staticmethod
    def create_agent(agent_type: str, model_name: str) -> ChatAgent:
        """Create an agent with the specified model."""
        return ChatAgent(model_name) 
