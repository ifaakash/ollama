import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:1.5b"

# 1. Setup the message history
messages = [
    {"role": "user", "content": "Hey Ollama! My name is Aakash. Just saying hello!"}
]

payload = {
    "model": MODEL,
    "messages": messages,
    "stream": False,
    "options": {
        "temperature": 0.7
    }
}

print(f"Sending chat request to {MODEL}...\n" + "-"*50)

try:
    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()
    
    api_response = response.json()
    
    # 2. Extract the AI's reply from the message object
    ai_reply = api_response.get("message", {}).get("content", "")
    
    print("\n--- AI Response ---")
    print(ai_reply)

except requests.exceptions.RequestException as e:
    print(f"API Request failed: {e}")
