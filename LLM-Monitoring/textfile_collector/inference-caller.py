'''
  Model
    architecture        qwen2    
    parameters          2B       
    context length      32768    
    embedding length    2048     
    quantization        Q4_0     
'''

import requests
import time
import os

OLLAMA_URL="http://localhost:11434/api/generate"
MODEL="qwen:1.8b"
PROMPT="What is internet Gateway in AWS?"

# context window for qwen1.8b
CTXW= 4000
INFERENCE_FILE = "/home/ubuntu/ollama/LLM-Monitoring/textfile_collector/inference.prom"
temperatures= [0.7]

print(f"Testing Model: {MODEL}\nPrompt: '{PROMPT}'\n" + "-"*50)


def track_inference_metrics(ollama_response_json, model_name="unknown"):
    """
    Takes the JSON response from an Ollama API call and exports TTFT and TPS.
    """
    try:
        # 1. Extract raw nanosecond metrics from the JSON
        prompt_eval_ns = ollama_response_json.get("prompt_eval_duration", 0)
        eval_duration_ns = ollama_response_json.get("eval_duration", 0)
        eval_count = ollama_response_json.get("eval_count", 0)
        
        # 2. Convert to seconds & calculate speeds
        ttft_sec = prompt_eval_ns / 1_000_000_000.0
        generation_time_sec = eval_duration_ns / 1_000_000_000.0
        
        # Prevent division by zero
        tps = (eval_count / generation_time_sec) if generation_time_sec > 0 else 0
        
        # 3. Format Prometheus payload 
        # Adding {model="name"} label so you can filter by model in Grafana!
        payload = f"""# HELP ollama_last_ttft_seconds Time to first token
# TYPE ollama_last_ttft_seconds gauge
ollama_last_ttft_seconds{{model="{model_name}"}} {ttft_sec:.4f}

# HELP ollama_last_tps Tokens per second
# TYPE ollama_last_tps gauge
ollama_last_tps{{model="{model_name}"}} {tps:.2f}

# HELP ollama_last_eval_count Tokens generated
# TYPE ollama_last_eval_count gauge
ollama_last_eval_count{{model="{model_name}"}} {eval_count}
"""
        # 4. Atomic write
        with open(INFERENCE_FILE, "w") as f:
            f.write(payload)
        
        # print(f"[Metrics Logged] Model: {model_name} | TPS: {tps:.2f} | TTFT: {ttft_sec:.2f}s")
        
    except Exception as e:
        print(f"Failed to track metrics: {e}")


for temp in temperatures:
    payload = {
        'prompt': PROMPT,
        'model': MODEL,
        'keep_alive': "30m",
        'options': {
            'temperature': temp,
            'num_ctx': CTXW
        },
        'stream': False
    }
    start_time= time.time()
    response = requests.post(OLLAMA_URL, json=payload)
    latency = round(time.time() - start_time, 2)
    if response.status_code == 200:
        result = response.json()
        print(f"Temperature: {temp}")
        print(f"Latency:     {latency}s")
        print(f"Output:      {result['response'].strip()}\n")
        print(f"Tokens:      {result['eval_count']}")
        print(f"Duration:    {result['eval_duration']/1000000000}s")
        track_inference_metrics(result, model_name= MODEL)
    else:
        print(f"Error hitting API: {response.status_code}")
