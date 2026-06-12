import ollama 
import requests 
import subprocess

aurl="http://localhost:11434/api/chat"
amodel="qwen2.5:1.5b"
amessages=[
    {
        'role': 'user',
        'content': 'What is the system temperature for raspberry pi?'
    }
]

def get_temp(username: str = 'anonymous', **kwargs):
    result = subprocess.run(
        ["vcgencmd", "measure_temp"], 
        capture_output=True, 
        text=True, 
        check=True
    )
    return result.stdout.strip()

available_tools= {
    'get_temp': get_temp
}

response=ollama.chat(
    model=amodel,
    messages=amessages,
    tools=[
        {
            'type':'function',
            'function': {
                'name': 'get_temp',
                'description': 'Get temperature of raspberry pi',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'username': {
                            'type': 'string',
                            'description': 'Name of user executing this command'
                        }
                    },
                    'required': ['username']
                }
            }
        }
    ]
)
print("INITIAL RESPONSE\n")
print(response)
#update_input_phase1= amessages.append(response.message)
print("\n\n")

print(amessages.append(response.message))

if response.message.tool_calls:
 for tool_call in response.message.tool_calls:
   func_name = tool_call.function.name
   func_args = tool_call.function.arguments
   if func_name in available_tools:
     tool_output = available_tools[func_name](**func_args)
     print("APPENDING TOOL CALL OUTPUT\n")
     updated_input_phase2= amessages.append({
        'role': 'tool',
        'name': func_name,
        'content': tool_output
     })
     print("UPDATED INPUT FOR LLM ---- FINAL PROMPT\n")
     print(amessages)
     final_response = ollama.chat(
        model=amodel,
        messages= amessages
     )
     print(final_response.message.content)
   else:
       print(">> No tools were called.")
       print(response.message.content)
else:
 print("RETRY")
