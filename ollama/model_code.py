import requests
import json
import os
import sys

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

def get_response(model_name: str, message: str) -> str:
    """
    Calls the Ollama API with the selected model and yields partial responses
    as they are generated.
    """
    if model_name not in available_models:
        yield f"Error: Model not found! Available models are: {', '.join(available_models.keys())}"
        return

    url = OLLAMA_REMOTE_URL
    payload = {
        "model": available_models[model_name],
        "prompt": message,
        "stream": True
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers, stream=True)
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                try:
                    json_data = json.loads(line)
                    if "response" in json_data:
                        yield json_data["response"]
                except json.JSONDecodeError:
                    pass

    except requests.exceptions.RequestException as e:
        yield f"Error: {str(e)}"
