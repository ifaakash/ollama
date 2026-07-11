import requests
import ollama

OLLAMA_URL="http://localhost:11434/api/chat"
METRIC_FILE = "/home/ubuntu/ollama/attention/monitoring/random-metric.prom"
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
    data = response.json()
    
    # Extract data
    message = data.get('message', {})
    model = data.get('model', 'unknown')
    
    # Convert nanoseconds to seconds for Prometheus
    total_duration_sec = data.get('total_duration', 0) / 1e9
    load_duration_sec = data.get('load_duration', 0) / 1e9
    prompt_eval_count = data.get('prompt_eval_count', 0)
    prompt_eval_duration_sec = data.get('prompt_eval_duration', 0) / 1e9
    eval_count = data.get('eval_count', 0)
    eval_duration_sec = data.get('eval_duration', 0) / 1e9


    tps= eval_count/eval_duration_sec
    tpot= eval_duration_sec/eval_count

    prompt_input_tps= prompt_eval_duration_sec/prompt_eval_count

    print(f"Prefill tps: ", prompt_input_tps*1000, 'token/sec')
    # print(f"Decode: ", tpot*1000, 'ms')    

    print(f"Message: {message}")
    print(f"Model: {model}")

    metrics_payload = f"""
# HELP ollama_request_total_duration_seconds Total time spent during generation
# TYPE ollama_request_total_duration_seconds gauge
ollama_request_total_duration_seconds{{model="{model}"}} {total_duration_sec}

# HELP ollama_request_load_duration_seconds Time spent loading the model
# TYPE ollama_request_load_duration_seconds gauge
ollama_request_load_duration_seconds{{model="{model}"}} {load_duration_sec}

# HELP ollama_prompt_eval_count Number of tokens in the prompt
# TYPE ollama_prompt_eval_count gauge
ollama_prompt_eval_count{{model="{model}"}} {prompt_eval_count}

# HELP ollama_prompt_eval_duration_seconds Time spent evaluating the prompt
# TYPE ollama_prompt_eval_duration_seconds gauge
ollama_prompt_eval_duration_seconds{{model="{model}"}} {prompt_eval_duration_sec}

# HELP ollama_eval_count Number of tokens generated in the response
# TYPE ollama_eval_count gauge
ollama_eval_count{{model="{model}"}} {eval_count}

# HELP ollama_eval_duration_seconds Time spent generating tokens
# TYPE ollama_eval_duration_seconds gauge
ollama_eval_duration_seconds{{model="{model}"}} {eval_duration_sec}
"""

    with open(METRIC_FILE, "w") as f:
        f.write(metrics_payload)
  else:
    printf(response.status_code)

except Exception as e:
  print("Got exception: ", {e})
