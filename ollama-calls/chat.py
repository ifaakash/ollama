import requests
import ollama

OLLAMA_URL="http://localhost:11434/api/chat"
MODEL="qwen2.5:1.5b"
PROMPT="Hey ollama! Can you say Hi to me? in a funny way"

payload= {
    'model': MODEL,
    'stream': False,
    'messages': [
        { 'role': 'user', 'content': PROMPT }
    ],
    'format': 'json',
    'keep_alive': '30m',
    'options': {
        'temperature': 0.7
    }
}

try:
  response = requests.post(OLLAMA_URL, json=payload)
  if response.status_code == 200:
    print(f"The response is: ", response.json())
  else:
    printf(response.status_code)

except Exception as e:
  print("Got exception: ", {e})
