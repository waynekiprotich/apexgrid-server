import requests
resp = requests.get("http://127.0.0.1:5001/api/v1/drivers?season=2024")
print(resp.status_code, resp.text)
