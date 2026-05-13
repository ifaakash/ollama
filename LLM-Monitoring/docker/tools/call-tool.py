import requests
import json
from prometheus import get_temp  # Assumes prometheus.py has get_temp()

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:1.5b"

def run_agent(user_prompt):
    # 1. Setup the Conversation and Tool Definitions
    messages = [{'role': 'user', 'content': user_prompt}]
    
    tools = [{
        "type": "function",
        "function": {
            "name": "get_system_health",
            "description": "Get real-time temperature from the Raspberry Pi 5.",
            "parameters": {"type": "object", "properties": {}}
        }
    }]

    payload = {
        'model': MODEL,
        'messages': messages,
        'tools': tools,
        'stream': False
    }

    try:
        # --- PASS 1: Ask Ollama if it needs a tool ---
        response = requests.post(OLLAMA_URL, json=payload)
        # If the status is NOT 200, print the raw body before raising the error
        if response.status_code != 200:
            print(f"--- OLLAMA ERROR DETAILS ---")
            print(response.text)  # This is the raw string from Ollama
            print(f"----------------------------")
            response.raise_for_status()

        result = response.json()
        print(result)
        print(f"#"*50)
        message = result.get('message', {})

        # 2. Check if Ollama requested a tool call
        if 'tool_calls' in message:
            print("Ollama: Intent detected. Running 'get_system_health'...")
            
            for tool_call in message['tool_calls']:
                if tool_call['function']['name'] == 'get_system_health':
                    # --- EXECUTION: Run your local Python function ---
                    temp_data = get_temp() 
                    
                    # 3. Build the context for the second pass
                    # Include the original tool request + the tool's answer
                    messages.append(message) 
                    messages.append({
                        'role': 'tool',
                        'content': str(temp_data),
                        'name': 'get_system_health'
                    })

                    # --- PASS 2: Send the data back for a final text answer ---
                    final_payload = {
                        'model': MODEL,
                        'messages': messages,
                        'stream': False
                    }
                    
                    final_res = requests.post(OLLAMA_URL, json=final_payload)
                    return final_res.json()['message']['content']

        # If no tool was needed, just return the text
        return message.get('content', "No response generated.")

    except requests.exceptions.RequestException as e:
        return f"Connection Error: {e}"

# --- Execution ---
user_query = "Is my Pi 5 running too hot right now?"
print(f"User: {user_query}")
answer = run_agent(user_query)
print(f"AI: {answer}")
