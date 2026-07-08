prompt="""
Hey ollama! My name is Aakash.
Please respond with a funny and short greeting message! Like wassup bro! keep a funny tone in all the chat
You must output your response in JSON format with the following keys:
- "user_name": the name of the user
- "greeting": your response message
"""

import tiktoken 
enc = tiktoken.get_encoding("o200k_base")

encoded= enc.encode(prompt)
print(encoded)
