import requests
import time
import json

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:1.5b"  # Upgraded from qwen:0.5b for native tool-use capability

# 1. Define the hardware call locally
def get_pi_temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp_millicelsius = int(f.read().strip())
            return f"{temp_millicelsius / 1000.0}°C"
    except Exception as e:
        return f"Error reading hardware thermal zones: {str(e)}"

# 2. Define the structural JSON schema for the tool (matches OpenAI tool specs)
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_pi_temperature",
            "description": "Get the current CPU temperature of the Raspberry Pi hardware unit.",
            "parameters": {
                "type": "object",
                "properties": {},  # No arguments needed for this function
                "required": []
            }
        }
    }
]

# 3. Create our running context window array
messages = [
    {
        "role": "system",
        "content": "You are an SRE assistant running locally. You have access to system diagnostics."
    },
    {
        "role": "user",
        "content": "Check the hardware temperature for me. Is the system running hot?"
    }
]

# --- FIRST API CALL: Ask the model if it needs a tool ---
payload = {
    "model": MODEL,
    "messages": messages,
    "tools": tools_schema,  # Pass the tool schema to the context
    "stream": False,
    "options": {
        "temperature": 0.1  # Low temperature keeps tool extraction deterministic
    }
}

print(f"Sending context window to {MODEL}...")
start_time = time.time()
response = requests.post(OLLAMA_URL, json=payload)
latency = round(time.time() - start_time, 2)

if response.status_code != 200:
    print(f"Error: {response.status_code} - {response.text}")
    exit()

result = response.json()
assistant_message = result["message"]

print(">> Response from Ollama…", assistant_message)
# Append the assistant's decision to our context tracking
messages.append(assistant_message)

print(f"Initial Latency: {latency}s")

# 4. Process the tool call if the model generated one
if "tool_calls" in assistant_message and assistant_message["tool_calls"]:
    print(">> The model requested a local hardware tool execution!")
    
    for tool_call in assistant_message["tool_calls"]:
        func_name = tool_call["function"]["name"]
        
        if func_name == "get_pi_temperature":
            print(f">> Executing local function: {func_name}()")
            tool_output = get_pi_temperature()
            print(f">> Tool Result Hooked: {tool_output}")
            
            # Append the execution result back into the context window
            messages.append({
                "role": "tool",
                "content": tool_output,
                "name": func_name
            })

    # --- SECOND API CALL: Send the results back so it can formulate an answer ---
    print("\n>> Sending tool results back to the model for final analysis...")
    final_payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False
    }
    
    final_response = requests.post(OLLAMA_URL, json=final_payload)
    if final_response.status_code == 200:
        final_result = final_response.json()
        print("\n--- Final SRE Agent Response ---")
        print(final_result["message"]["content"])
        print(f"Tokens generated in final phase: {final_result['eval_count']}")
    else:
        print("Error getting final analysis from model.")
else:
    print(">> The model answered directly without requesting any tools:")
    print(assistant_message["content"])
