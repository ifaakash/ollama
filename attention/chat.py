import requests
import ollama

OLLAMA_URL="http://localhost:11434/api/chat"
MODEL="qwen2.5:1.5b"
PROMPT = """
Hey ollama! My name is Aakash. 
Please respond with a funny and short greeting message! Like wassup bro! keep a funny tone in all the chat
You must output your response in JSON format with the following keys:
- "user_name": the name of the user
- "greeting": your response message
"""

payload= {
    'model': MODEL,
    'stream': False,
    'messages': [
        { 'role': 'user', 'content': PROMPT }
    ],
    'format': 'json',
    'keep_alive': '60m',
    'options': {
        'temperature': 0.7
    }
}

try:
  response = requests.post(OLLAMA_URL, json=payload)
  if response.status_code == 200:
    response= response.json()
    # print(f"The response is: ", response)
    print(f"Message: ", response.get('message'))
    print(f"Model:\t", response.get('model'))
    print(f"Total duration:\t", response.get('total_duration')/1000000000) # Total time spend during generation
    print(f"Load duration:\t", response.get('load_duration')/1000000000) # Time spent loading the model
    print(f"Prompt Tokens count:\t", response.get('prompt_eval_count')) # Number of tokens in the prompt
    print(f"Prompt evaluation duration :", response.get('prompt_eval_duration')/1000000000) # Time spent evaluating the prompt
    print(f"Output token count:\t", response.get('eval_count')) # Number of tokens generated in the response    
    print(f"Output token evaluation duration:\t", response.get('eval_duration')/1000000000) # Time spent generating tokens
  else:
    printf(response.status_code)

except Exception as e:
  print("Got exception: ", {e})
