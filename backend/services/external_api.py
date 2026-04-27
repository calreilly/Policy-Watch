import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

logger = logging.getLogger(__name__)

class CongressAPIClient:
    """HTTP client for Congress.gov API with exponential backoff and timeout handling."""
    def __init__(self, base_url: str = "https://api.congress.gov/v3", timeout: float = 10.0):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=self.timeout)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError, httpx.HTTPStatusError))
    )
    async def fetch(self, path: str, params: dict = None) -> dict:
        """GET request with retry on timeout, connection errors, and rate‑limit (429)."""
        url = f"{self.base_url}{path}"
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429:
                logger.warning("Rate limited by Congress.gov; will retry with backoff")
                raise
            logger.error(f"Congress API error {exc.response.status_code}: {exc.response.text}")
            raise
        except Exception as exc:
            logger.error(f"Unexpected error contacting Congress API: {exc}")
            raise

    async def close(self):
        await self.client.aclose()
