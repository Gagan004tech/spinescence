import requests
import json

url = "http://localhost:8000/forecast?commodity=cardamom"
try:
    response = requests.get(url, timeout=30)
    print("Status Code:", response.status_code)
    try:
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
    except BaseException as e:
        print("Failed to parse JSON:", response.text)
except Exception as e:
    print("Request failed:", e)
