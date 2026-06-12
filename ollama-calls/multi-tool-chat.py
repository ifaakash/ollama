import ollama

amodel = 'qwen2.5:1.5b'

# 1. Define two simple Python functions
def get_cpu_temp(username: str) -> str:
    print(f"\n[TOOL] Executing get_cpu_temp for: {username}")
    return "48.2°C"

def get_fan_speed(username: str) -> str:
    print(f"\n[TOOL] Executing get_fan_speed for: {username}")
    return "2500 RPM"

# Map function names to the callable Python functions
available_tools = {
    'get_cpu_temp': get_cpu_temp,
    'get_fan_speed': get_fan_speed
}

# 2. Setup the initial user prompt asking for BOTH metrics
messages = [
    {
        'role': 'user',
        'content': 'What is the CPU temperature and the fan speed of the Raspberry Pi? My username is dev_user.'
    }
]

# 3. First call to Ollama with BOTH tool schemas
print(">> Step 1: Sending prompt to LLM...")
response = ollama.chat(
    model=amodel,
    messages=messages,
    tools=[
        {
            'type': 'function',
            'function': {
                'name': 'get_cpu_temp',
                'description': 'Get the CPU temperature of the Raspberry Pi',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'username': {
                            'type': 'string',
                            'description': 'username of the requester'
                        }
                    },
                    'required': ['username']
                }
            }
        },
        {
            'type': 'function',
            'function': {
                'name': 'get_fan_speed',
                'description': 'Get the fan speed of the Raspberry Pi',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'username': {
                            'type': 'string',
                            'description': 'username of the requester'
                        }
                    },
                    'required': ['username']
                }
            }
        }
    ]
)

# Append the assistant's response (which contains the tool call requests)
messages.append(response.message)

# 4. Check and execute any requested tool calls
if response.message.tool_calls:
    print(f">> Step 2: {len(response.message.tool_calls)} tool calls detected!")
    
    for tool_call in response.message.tool_calls:
        func_name = tool_call.function.name
        func_args = tool_call.function.arguments  # This is a dictionary of arguments
        
        if func_name in available_tools:
            # Execute the function with the unpacked arguments from the model
            tool_output = available_tools[func_name](**func_args)
            
            # Append each execution output to the conversation history
            messages.append({
                'role': 'tool',
                'name': func_name,
                'content': tool_output
            })
            
    # 5. Second call to Ollama: Give it the tool outputs to summarize
    print("\n>> Step 3: Sending tool results back to LLM...")
    final_response = ollama.chat(
        model=amodel,
        messages=messages
    )
    
    print("\n--- Final AI Response ---")
    print(final_response.message.content)
else:
    print(">> No tools were called.")
    print(response.message.content)
