import time
from typing import Any, Dict, Optional, Tuple

import requests
from requests.exceptions import ReadTimeout, SSLError, ConnectionError as ReqConnectionError


RetryableExc = (ReadTimeout, SSLError, ReqConnectionError)


class JsonRpcClient:
    """
    Lightweight JSON-RPC client with:
      - configurable timeout
      - optional retries for retryable failures (timeout/ssl/connection)
    """

    def __init__(self, rpc_url: str, timeout_s: int = 15, retries: int = 1, proxy: Optional[str] = None):
        self.rpc_url = rpc_url
        self.timeout_s = timeout_s
        self.retries = max(0, int(retries))
        self.session = requests.Session()
        self.proxies = {"http": proxy, "https": proxy} if proxy else None

    def call(
        self, method: str, params: Any, request_id: int
    ) -> Tuple[Optional[Dict[str, Any]], int, Optional[str], int]:
        """
        Returns: (data, latency_ms, error_str, attempt)
        attempt is 1-based.
        """
        payload = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}

        last_err: Optional[str] = None
        last_latency_ms = 0

        for attempt in range(1, 2 + self.retries):
            t0 = time.time()
            try:
                r = self.session.post(
                    self.rpc_url,
                    json=payload,
                    timeout=self.timeout_s,
                    proxies=self.proxies,
                )
                last_latency_ms = int((time.time() - t0) * 1000)
                r.raise_for_status()
                data = r.json()
                if "error" in data:
                    # JSON-RPC error from endpoint
                    return data, last_latency_ms, "rpc_error", attempt
                return data, last_latency_ms, None, attempt

            except RetryableExc as e:
                last_latency_ms = int((time.time() - t0) * 1000)
                last_err = f"exception:{type(e).__name__}:{str(e)[:120]}"
                # retry if attempts remain
                if attempt < 1 + self.retries:
                    continue
                return None, last_latency_ms, last_err, attempt

            except Exception as e:
                last_latency_ms = int((time.time() - t0) * 1000)
                last_err = f"exception:{type(e).__name__}:{str(e)[:120]}"
                return None, last_latency_ms, last_err, attempt

        # Should not reach
        return None, last_latency_ms, last_err, 1