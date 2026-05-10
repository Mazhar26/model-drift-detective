import requests
from config import API_HOST, API_PORT

# Build base URL from centralized config with API version prefix
BASE_URL = f"http://{API_HOST}:{API_PORT}/api/v1"


def fetch_data(endpoint, params=None):
    """
    Fetch JSON data from the FastAPI backend (versioned API).

    Args:
        endpoint: API endpoint name (without leading slash or version prefix).
                  Example: "detect", "summary", "explain"
        params: Optional query parameters dict.

    Returns:
        Parsed JSON response as dict/list, or empty dict on failure.
    """
    try:
        url = f"{BASE_URL}/{endpoint}"
        res = requests.get(url, params=params, timeout=30)
        if res.status_code == 200:
            return res.json()
        return {}
    except requests.exceptions.ConnectionError:
        return {}
    except requests.exceptions.Timeout:
        return {}
    except Exception:
        return {}