import ollama
import requests

amodel="qwen2.5:1.5b"
aprompt = """
What is the temperature of raspberry pi You must output your response in JSON format with the following keys:
- "user_name": the name of the user
- "greeting": your response message
"""

aurl="http://localhost:11434/api/chat"

apayload= {
    'model': amodel,
    'messages': [
        {
          'role': "user",
          'content': aprompt
        }
    ],
    'stream': False,
    'keep_alive': '60m',
    'format': 'json',
   # 'options' : {},
    'tools': [ {
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
}

response = requests.post(aurl, json=apayload)

if response.status_code == 200:
  print("OLLAMA RESPONE")
  print(response.json())
else:
  print("OLLAMA CALL FAILED")
  print(response.status_code)
