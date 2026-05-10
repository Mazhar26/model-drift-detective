import requests

BASE_URL = "http://127.0.0.1:8000"

def fetch_data(endpoint, params=None):
    try:
        res = requests.get(f"{BASE_URL}/{endpoint}", params=params)
        if res.status_code == 200:
            return res.json()
        return {}
    except:
        return {}