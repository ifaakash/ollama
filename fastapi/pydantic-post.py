from pydantic import BaseModel
from fastapi import FastAPI

aollama_url="http://localhost:11434/api/chat"
amodel="qwen2.5:1.5b"


class ChatRequest(BaseModel):
    prompt: str
    temperature: float = 0.7

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "alive"}

@app.post("/chat")
def chat(req: ChatRequest):
    apayload= {
        'model': amodel,
        'stream': False,
        'messages': [
            { 'role': 'user', 'content': req.prompt }
        ],
        'format': 'json',
        'keep_alive': '30m',
        'options': {
            'temperature': req.temperature
        }
    }
    
    try:
        response = requests.post(aollama_url, json=apayload)
        if response.status_code == 200:
            data = response.json()
            message = data.get('message', {})
    return {"response": message}
#    return {"received": req.prompt, "temp": req.temperature}
