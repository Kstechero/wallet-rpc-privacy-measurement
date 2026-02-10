import time
import os
import yaml
from datetime import datetime
from typing import Dict, Any, List

from rpc_client import JsonRpcClient
from scenarios import scenario_blocknumber, scenario_balance, scenario_nonce, scenario_call_example
from logger import build_log_record, append_jsonl

def load_addresses(path: str) -> List[str]:
    addrs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s and s.startswith("0x") and len(s) == 42:
                addrs.append(s)
    return addrs

def main():
    cfg_path = os.environ.get("EXP_CONFIG", "configs/exp_sepolia_providerA.yaml")
    cfg: Dict[str, Any] = yaml.safe_load(open(cfg_path, "r", encoding="utf-8"))

    rpc_url = cfg["rpc_url"]
    provider_id = cfg.get("provider_id", "provider")
    chain_id = cfg.get("chain_id", 11155111)
    duration_s = int(cfg.get("duration_s", 60))
    interval_s = float(cfg.get("interval_s", 2.0))
    scenario = cfg.get("scenario", "blocknumber")
    proxy = cfg.get("proxy", None)

    addresses = load_addresses(cfg["addresses_file"]) if "addresses_file" in cfg else []

    # output log path
    run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_path = cfg.get("out_log", f"logs/run_{provider_id}_{run_id}.jsonl")

    client = JsonRpcClient(rpc_url, timeout_s=30, proxy=proxy)

    # choose scenario
    if scenario == "blocknumber":
        ops = scenario_blocknumber()
    elif scenario == "balance":
        ops = scenario_balance(addresses)
    elif scenario == "nonce":
        ops = scenario_nonce(addresses)
    elif scenario == "call":
        ops = scenario_call_example()
    else:
        raise ValueError(f"Unknown scenario: {scenario}")

    t_end = time.time() + duration_s
    req_id = 1
    while time.time() < t_end:
        for (method, params) in ops:
            base = {
                "ts_ms": int(time.time() * 1000),
                "provider_id": provider_id,
                "rpc_url": rpc_url,
                "chain_id": chain_id,
                "scenario": scenario
            }
            data, latency_ms, err = client.call(method, params, req_id)
            status = "ok" if (data is not None and err is None) else "error"
            rec = build_log_record(base, method, params, latency_ms, status, err)
            append_jsonl(out_path, rec)
            req_id += 1

        time.sleep(interval_s)

    print(f"Done. Log saved to {out_path}")

if __name__ == "__main__":
    main()
