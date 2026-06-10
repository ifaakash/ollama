import ollama
import requests

amodel='qwen2.5:1.5b'
aprompt = """
What is the temperature of raspberry pi You must output your response in JSON format with the following keys:
- "user_name": the name of the user
- "greeting": your response message
"""

aurl="http://localhost:11434/api/chat"

response = ollama.chat(
    'model'= amodel,
    'messages'= [
        {
          'role': "user",
          'content': aprompt
        }
    ],
    'stream'= False,
    'keep_alive'= '60m',
    'format'= 'json',
   # 'options' : {},
    'tools'= [ {
      'type'= 'function',
      'function'= {
        'name'= 'get_temp',
        'description'= 'Get hardware temperature of raspberry pi',
        'parameters'= {
            'type'= 'object',
            'properties'= {
                'username'= {
                    'type'= 'string',
                    'description'= 'username executing the job'
                }
            },
            'required'= ['username'],
        }
      }
    }
 ]
)

print(response)
