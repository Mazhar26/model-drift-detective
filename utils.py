import requests
from config import API_HOST, API_PORT
from logger import get_logger

logger = get_logger(__name__)

# Automatically use HTTPS for Render deployments
if "onrender.com" in API_HOST:
    BASE_URL = f"https://{API_HOST}/api/v1"
else:
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
        logger.error("Connection failed to backend: %s", url)
        return {}

    except requests.exceptions.Timeout:
        logger.warning("Request timeout: %s", url)
        return {}

    except requests.exceptions.HTTPError as e:
        logger.warning("HTTP error: %s", e)
        return {}

    except requests.exceptions.JSONDecodeError:
        logger.warning("Invalid JSON response from: %s", url)
        return {}

    except Exception as e:
        logger.error("Unexpected error: %s", e)
        return {}