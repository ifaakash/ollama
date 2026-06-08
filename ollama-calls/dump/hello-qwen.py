import json
import ollama

MODEL = "qwen2.5:1.5b"

# Because we are using 'format': 'json', we must ask for JSON in the prompt
PROMPT = """
Hey ollama! My name is Aakash. 
Please respond with a polite greeting. 
You must output your response in JSON format with the following keys:
- "user_name": the name of the user
- "greeting": your response message
"""

print(f"Testing Model: {MODEL} via ollama.generate()...\n" + "-"*50)

try:
    # ollama.generate hits the /api/generate endpoint under the hood
    response = ollama.generate(
        model=MODEL,
        prompt=PROMPT,
        format='json',  # Enforces strict JSON output
        options={
            'temperature': 0.7,
            'top_p': 0.9
        },
        keep_alive='15m'
    )
    
    # 1. Extract the raw stringified JSON from the response
    ai_string_output = response['response']
    print(response.json())
    print( "-"*50)
    # 2. Parse it into a Python dictionary
    parsed_json = json.loads(ai_string_output)
    
    print("\n--- Parsed AI Response ---")
    print(f"User Name: {parsed_json.get('user_name')}")
    print(f"Greeting:  {parsed_json.get('greeting')}")

except Exception as e:
    print(f"An error occurred: {e}")
