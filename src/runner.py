import os
import time
import yaml
from datetime import datetime, timezone
from typing import Any, Dict, List

from rpc_client import JsonRpcClient
from scenarios import (
    scenario_blocknumber,
    scenario_balance,
    scenario_nonce,
    scenario_call_example,
    scenario_estimate_gas,
)
from logger import build_log_record, append_jsonl


def load_addresses(path: str) -> List[str]:
    addrs: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s and s.startswith("0x") and len(s) == 42:
                addrs.append(s)
    return addrs


def ensure_parent_dir(path: str) -> None:
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)


def run_from_config(cfg_path: str) -> str:
    cfg: Dict[str, Any] = yaml.safe_load(open(cfg_path, "r", encoding="utf-8"))

    rpc_url = cfg["rpc_url"]
    provider_id = cfg.get("provider_id", "provider")
    chain_id = int(cfg.get("chain_id", 11155111))
    duration_s = int(cfg.get("duration_s", 60))
    interval_s = float(cfg.get("interval_s", 5.0))
    scenario = cfg.get("scenario", "blocknumber")
    proxy = cfg.get("proxy", None)
    timeout_s = int(cfg.get("timeout_s", 15))
    retries = int(cfg.get("retries", 1))
    repeat_id = cfg.get("repeat_id", None)

    addresses = load_addresses(cfg["addresses_file"]) if "addresses_file" in cfg else []

    # output path: prefer explicit out_log
    out_path = cfg.get("out_log")
    if not out_path:
        run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        rep = f"rep{repeat_id}" if repeat_id is not None else "rep1"
        out_path = f"logs/{provider_id}_{scenario}_int{interval_s}_{rep}_{run_id}.jsonl"

    ensure_parent_dir(out_path)

    # Avoid log pollution: always start fresh for this run
    if os.path.exists(out_path):
        os.remove(out_path)

    client = JsonRpcClient(rpc_url, timeout_s=timeout_s, retries=retries, proxy=proxy)

    # choose scenario ops
    if scenario == "blocknumber":
        ops = scenario_blocknumber()
    elif scenario == "balance":
        ops = scenario_balance(addresses)
    elif scenario == "nonce":
        ops = scenario_nonce(addresses)
    elif scenario == "call":
        ops = scenario_call_example()
    elif scenario == "estimateGas":
        ops = scenario_estimate_gas(addresses)
    else:
        raise ValueError(f"Unknown scenario: {scenario}")

    t_end = time.time() + duration_s
    req_id = 1

    # store experiment metadata in each record
    exp_meta = {
        "provider_id": provider_id,
        "rpc_url": rpc_url,
        "chain_id": chain_id,
        "scenario": scenario,
        "duration_s": duration_s,
        "interval_s": interval_s,
        "repeat_id": repeat_id,
    }

    while time.time() < t_end:
        for (method, params) in ops:
            base = {
                "ts_ms": int(time.time() * 1000),
                **exp_meta,
            }

            data, latency_ms, err, attempt = client.call(method, params, req_id)
            status = "ok" if (data is not None and err is None) else "error"

            rec = build_log_record(
                base=base,
                method=method,
                params=params,
                latency_ms=latency_ms,
                status=status,
                error=err,
                attempt=attempt,
                data=data,
            )
            append_jsonl(out_path, rec)
            req_id += 1

        time.sleep(interval_s)

    print(f"Done. Log saved to {out_path}")
    return out_path


def main() -> None:
    cfg_path = os.environ.get("EXP_CONFIG", "configs/exp_sepolia_providerA.yaml")
    run_from_config(cfg_path)


if __name__ == "__main__":
    main()