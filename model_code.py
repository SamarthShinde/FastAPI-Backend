import requests
import json
from config import OLLAMA_REMOTE_URL

available_models = {
    "llama3.2": "llama3.2",
    "llama3.3": "llama3.3",
    "deepseek-r1:70b": "deepseek-r1:70b",
    "phi4": "phi4"
}

def get_response(model_name: str, message: str) -> str:
    """
    Calls the Ollama API with the selected model and yields partial responses
    as they are generated.
    """
    if model_name not in available_models:
        yield "Error: Model not found!"
        return

    url = f"{OLLAMA_REMOTE_URL}"
    payload = {
        "model": available_models[model_name],
        "prompt": message
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers, stream=True)
        response.raise_for_status()

        # Process streamed response and yield each partial output
        for line in response.iter_lines():
            if line:
                try:
                    json_data = json.loads(line)
                    if "response" in json_data:
                        yield json_data["response"] + " "
                except json.JSONDecodeError:
                    pass  # Ignore decoding errors from partial JSON lines

    except requests.exceptions.RequestException as e:
        yield f"Request failed: {str(e)}"