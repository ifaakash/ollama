from prometheus import get_temp

OLLAMA_URL="http://localhost:11434/api/chat"
tools = [{
    "type": "function",
    "function": {
        "name": "get_system_health",
        "description": "Get real-time temperature from the Raspberry Pi 5.",
        "parameters": {"type": "object", "properties": {}}
    }
}]

MODEL="qwen:1.8b"
payload = {
    'model': MODEL,
    # REPLACE 'prompt' with 'messages'
    'messages': [
        {'role': 'user', 'content': PROMPT}
    ],
    # ADD tools
    'tools': tools, 
    'options': {
        "temperature": temp,
        "top_p": 0.9
    },
    "keep_alive": "15m",
    "stream": False
}

def run_agent(user_prompt):
   try:
     response=requests.get(OLLAMA_URL,json=payload)
     if response.status_code==200:
        return response.json()
     else:
        return_code = response.status_code
        return f"Connection eror with code {return_code}"
   except requests.exceptions.RequestException as e:
        print(f"Connection Error: {e}")

print("Ollama wants to run a script!")
run_agent()
