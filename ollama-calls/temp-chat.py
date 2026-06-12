import ollama

amodel = 'qwen2.5:1.5b'
aprompt = """
What is the temperature of raspberry pi? Use the tool mentioned in the tool calls. You must output your response in JSON format with the following keys:
- "user_name": the name of the user
- "greeting": your response message
"""

# Keep track of your conversation history in a list
messages = [
    {
        'role': 'user',
        'content': aprompt
    }
]

response = ollama.chat(
    model=amodel,
    messages=messages,
    stream=False,
    keep_alive='60m',
    tools=[
        {
            'type': 'function',
            'function': {
                'name': 'get_temp',
                'description': 'Get hardware temperature of raspberry pi',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'username': {
                            'type': 'string',
                            'description': 'username executing the job'
                        }
                    },
                    'required': ['username'],
                }
            }
        }
    ]
)

def get_temp():
    return "Temperature is 50 degree celsius"

print(response['message']['tool_calls'])

if response.message.tool_calls:
    print("TOOL CALL DETECTED")
    tool_name = response.message.tool_calls[0].function.name
    
    if tool_name == 'get_temp':
        # 1. Execute your function
        output = get_temp()
        
        # 2. Append the model's tool call request to the conversation history
        messages.append(response.message)
        
        # 3. Append the execution result as a 'tool' role message
        messages.append({
            'role': 'tool',
            'name': tool_name,
            'content': output
        })
        
        # 4. Call Ollama a second time with the complete history to get the final answer
        final_response = ollama.chat(
            model=amodel,
            messages=messages,
            format='json'  # Restrict final response to JSON
        )
        
        print("\n--- Final AI Response ---")
        print(final_response.message.content)
        
    else:
        print(f"{tool_name} tool called but not matched") 
else:
    print("TRY BETTER!")
