import requests

url = "http://100.76.6.76:4000/spend/logs"

params = {
    "api_key": "qwertyuiop",
    "summarize": "true"
}

headers = {
    "accept": "application/json",
    "x-litellm-api-key": "qwertyuiop"
}

response = requests.get(url, params=params, headers=headers)

if response.status_code==200:
   print(response.json())
else:
   print(f"Failed with status code: {response.status_code}")
