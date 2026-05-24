import requests
from config import API_HOST, API_PORT

# Centralized versioned API base URL
BASE_URL = f"http://{API_HOST}:{API_PORT}/api/v1"


def fetch_data(endpoint, params=None):
    """
    Fetch JSON data from the FastAPI backend.

    Args:
        endpoint (str):
            API endpoint name without leading slash.
            Example: "detect", "impact", "summary"

        params (dict, optional):
            Query parameters for the request.

    Returns:
        dict | list:
            Parsed JSON response from backend.
            Returns empty dict on failure.
    """

    try:
        url = f"{BASE_URL}/{endpoint}"

        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.ConnectionError:
        print(f"❌ Connection failed to backend: {url}")
        return {}

    except requests.exceptions.Timeout:
        print(f"⏳ Request timeout: {url}")
        return {}

    except requests.exceptions.HTTPError as e:
        print(f"⚠️ HTTP error: {e}")
        return {}

    except requests.exceptions.JSONDecodeError:
        print(f"⚠️ Invalid JSON response from: {url}")
        return {}

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return {}