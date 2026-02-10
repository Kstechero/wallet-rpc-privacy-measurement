import json
import hashlib
from typing import Any, Dict, Optional

def _hash_params(params: Any) -> str:
    s = json.dumps(params, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]

def _contains_hex_address(params: Any) -> bool:
    # heuristic: 0x + 40 hex chars
    def check_str(x: str) -> bool:
        if not isinstance(x, str):
            return False
        if len(x) != 42:
            return False
        if not x.startswith("0x"):
            return False
        try:
            int(x[2:], 16)
            return True
        except Exception:
            return False

    if isinstance(params, str):
        return check_str(params)
    if isinstance(params, list):
        return any(_contains_hex_address(p) for p in params)
    if isinstance(params, dict):
        return any(_contains_hex_address(v) for v in params.values())
    return False

def build_log_record(
    base: Dict[str, Any],
    method: str,
    params: Any,
    latency_ms: int,
    status: str,
    error: Optional[str]
) -> Dict[str, Any]:
    rec = dict(base)
    rec.update({
        "method": method,
        "params_hash": _hash_params(params),
        "has_address": _contains_hex_address(params),
        "latency_ms": latency_ms,
        "status": status,
        "error": error
    })
    return rec

def append_jsonl(path: str, record: Dict[str, Any]) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
