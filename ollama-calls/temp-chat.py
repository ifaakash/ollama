import ollama
import requests

amodel = 'qwen2.5:1.5b'
aprompt = """
What is the temperature of raspberry pi? Use the tool mentioned in the tool calls. You must output your response in JSON format with the following keys:
- "user_name": the name of the user
- "greeting": your response message
"""

aurl = "http://localhost:11434/api/chat"

response = ollama.chat(
    model=amodel,
    messages=[
        {
            'role': "user",
            'content': aprompt
        }
    ],
    stream=False,
    keep_alive='60m',
    # options={},
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
 return "Temperatue is 50 degree celsius"

print(response['message']['tool_calls'])

if response.message.tool_calls:
 print("TOOL CALL DETECTED")
 tool_name = response.message.tool_calls[0].function.name
 if tool_name == 'get_temp':
   output=  get_temp()
   aprompt.append(output)
 else:
  print(f"${tool_name} tool called") 
else:
 print("TRY BETTER!")

