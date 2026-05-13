import requests

PROMETHEUS_URL="http://localhost:9090/api/v1/query"
PARAMS={"query": "pi5_custom_temperature_celsius"}

def get_temp():
   response= requests.get(PROMETHEUS_URL,params= PARAMS)
   if response.status_code ==200:
      print(response.json())
   else:
      print("Error!")

get_temp()
