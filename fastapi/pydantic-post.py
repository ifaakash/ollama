from pydantic import BaseModel
from fastapi import FastAPI
import requests 
import time
import asyncio
import httpx

aollama_url="http://localhost:11434/api/chat"
amodel="qwen2.5:1.5b"


class ChatRequest(BaseModel):
    prompt: str
    temperature: float = 0.7

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "alive"}

@app.get("/sleep")
async def sleep_test():
    start = time.perf_counter()
    await asyncio.sleep(8)
    return {"latency_s": round(time.perf_counter() - start, 2)}

@app.post("/debug")
async def debug(req: ChatRequest):
    apayload= {
        'model': amodel,
        'stream': False,
        'messages': [
            { 'role': 'user', 'content': req.prompt }
        ],
        # 'format': 'json',
        'keep_alive': '30m',
        'options': {
            'temperature': req.temperature
        }
    }

    # 1. Initialize your local variable with a safe default
    message = {"error": "Failed to get a response"}
    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(aollama_url, json=apayload)
            if response.status_code == 200:
                data = response.json()
                llm_response = data.get("response", {})
                result = {
                    "promp_eval_count"= llm_response.get("prompt_eval_count",0 )
                    "output_token_count" =  llm_response.get("eval_count",0)
                }
    except Exception as e:
        message = {"error": str(e)}
    elapsed = time.perf_counter() - start
    return {"response": result, "latency_s": round(elapsed, 2)}
    

@app.post("/chat")
async def chat(req: ChatRequest):
    apayload= {
        'model': amodel,
        'stream': False,
        'messages': [
            { 'role': 'user', 'content': req.prompt }
        ],
        # 'format': 'json',
        'keep_alive': '30m',
        'options': {
            'temperature': req.temperature
        }
    }

    # 1. Initialize your local variable with a safe default
    message = {"error": "Failed to get a response"}
    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(aollama_url, json=apayload)
            if response.status_code == 200:
                message = response.json().get('message', {})
                print(message)
#    try:
#        response = requests.post(aollama_url, json=apayload)
#        if response.status_code == 200:
#            elapsed = time.perf_counter() - start
#            data = response.json()
#            message = data.get('message', {})
    except Exception as e:
        message = {"error": str(e)}
    elapsed = time.perf_counter() - start
    return {"response": message.get('content'), "latency_s": round(elapsed, 2)}
    
#    return {"received": req.prompt, "temp": req.temperature}


import json
from fastapi.responses import StreamingResponse

@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    apayload = {
        'model': amodel,
        'stream': True,   # <-- the Ollama-side flip
        'messages': [{'role': 'user', 'content': req.prompt}],
        'keep_alive': '30m',
        'options': {'temperature': req.temperature}
    }

    async def token_generator():
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                async with client.stream("POST", aollama_url, json=apayload) as response:
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        obj = json.loads(line)
                        yield obj.get("message", {}).get("content", "")
        except Exception as e:
            yield f"\n[error: {e}]"

    return StreamingResponse(token_generator(), media_type="text/plain")
