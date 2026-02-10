import requests
import time
from typing import Any, Dict, Optional, Tuple

class JsonRpcClient:
    def __init__(self, rpc_url: str, timeout_s: int = 30, proxy: Optional[str] = None):
        self.rpc_url = rpc_url
        self.timeout_s = timeout_s
        self.session = requests.Session()
        self.proxies = {"http": proxy, "https": proxy} if proxy else None

    def call(self, method: str, params: Any, request_id: int) -> Tuple[Optional[Dict[str, Any]], int, Optional[str]]:
        payload = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
        t0 = time.time()
        try:
            r = self.session.post(
                self.rpc_url,
                json=payload,
                timeout=self.timeout_s,
                proxies=self.proxies
            )
            latency_ms = int((time.time() - t0) * 1000)
            r.raise_for_status()
            data = r.json()
            if "error" in data:
                return data, latency_ms, "rpc_error"
            return data, latency_ms, None
        except Exception as e:
            latency_ms = int((time.time() - t0) * 1000)
            return None, latency_ms, f"exception:{type(e).__name__}"
