# Wallet–RPC Privacy Leakage Measurement (Empirical Study)

## 1. Background
In Ethereum and other EVM ecosystems, user wallets (e.g., MetaMask) typically do not maintain a full node locally. Instead, they rely on third-party or public RPC (JSON-RPC) endpoints to read on-chain data, simulate contract calls, and broadcast transactions.

This creates potential privacy risks: RPC providers (and observers along the network path) may profile user behavior based on request metadata and semantics (e.g., method type, timestamps, request frequency, and whether address parameters appear), and may attempt multi-address linkage (linkability) inference.

The goal of this project is to conduct an **empirical measurement** of these risks by running controlled workloads across different RPC providers, collecting structured logs, and computing metrics to support evidence-based conclusions.

---

## 2. Problem Statement
This project aims to measure and quantify the privacy-relevant information that may be leaked through wallet RPC requests, and to compare different RPC providers along these dimensions:

- **Availability:** success rate, timeout rate, error types
- **Performance:** latency distribution (median / average / p95 / max, etc.)
- **Privacy exposure proxies:**
  - method distribution (what actions the user is performing)
  - presence of address-bearing requests (`has_address`)
  - request cadence/frequency (behavioral signatures)

---

## 3. Scope

### Milestone 1 (Baseline)
- **Network:** Sepolia testnet (`chain_id = 11155111`)
- **Scenarios:**
  - `blocknumber`: calls `eth_blockNumber` (address-free baseline)
  - `balance`: calls `eth_getBalance` (address-bearing; address exposure proxy)
- **Comparison targets:** at least two RPC endpoints (providerA/providerB)
- **Data output:** JSONL (one JSON record per RPC request)

### Milestone 2 (Matrix Experiments)
- **Network:** Sepolia testnet (`chain_id = 11155111`)
- **Scenarios:** `blocknumber`, `balance`, `nonce`, `call`, `estimateGas`
- **Experiment matrix:** provider (A/B) × interval (`int1`, `int5`) × replicate (`rep1`–`rep3`)
- **Outputs:**
  - JSONL logs for each run (configured via `out_log`)
  - `summary.csv` consolidated across all runs (written by `batch_run.py`)

Out of scope (possible later extensions):
- transaction broadcasting, DeFi/NFT interactions, WebSocket subscriptions
- traffic interception/proxy analysis (Wireshark / mitmproxy) for network-layer metadata
- advanced multi-address correlation algorithms and scoring models

---

## 4. Threat Model (v1, brief)
Potential attackers/observers:
- RPC providers (logging and aggregating requests)
- network eavesdroppers / MITM observers (timing and connection observations)
- malicious RPC node operators (active collection and analysis)
- data analytics companies (cross-service correlation)

Primary attack vectors (measurable in the current phase):
- **metadata leakage:** timestamps, frequency, latency, error patterns
- **semantic leakage:** method types, presence of addresses / contract interaction traces
- **linkage inference:** behavioral patterns across multiple addresses from the same source (later extension)

---

## 5. What is the Measurement Harness?
This project implements a reproducible **measurement harness** that:
- reads YAML configs specifying network, `rpc_url`, `scenario`, duration, interval, etc.
- issues JSON-RPC requests according to a scenario definition (e.g., `eth_blockNumber`, `eth_getBalance`)
- logs per-request metadata into JSONL
- runs identical workloads across providers for A/B comparison
- summarizes logs via `summarize.py` and aggregates batch results via `batch_run.py`

In one sentence: the harness is an automated framework that enables repeatable experiments and produces analyzable outputs.

---

## 6. Project Structure

- `configs/`
  - `m1/`: archived Milestone 1 baseline configs
  - `m2/`: Milestone 2 matrix experiment configs
  - `addresses_demo.txt`: address list for address-bearing scenarios (one `0x...` per line)
- `src/`
  - `runner.py`: entry point; loads config, runs one experiment, writes logs
  - `rpc_client.py`: JSON-RPC client (HTTP)
  - `scenarios.py`: scenario definitions and parameter construction
  - `logger.py`: constructs and appends JSONL records
  - `summarize.py`: summarizes a JSONL log into metrics
  - `batch_run.py`: runs a set of configs and writes/updates `summary.csv`
- `logs/`
  - runtime-generated JSONL logs (recommended to ignore in Git or commit only de-identified samples)
- `results/`
  - optional derived outputs (if you choose to separate `summary.csv` into `results/`)

---

## 7. Quick Start

### 7.1 Setup
```bash
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
mkdir logs
```

### 7.2 Run a single experiment (one config)
Example: providerA blocknumber
```bash
EXP_CONFIG=configs/m2/A_blocknumber_int1_rep1.yaml python src/runner.py
```

Example: providerA balance (requires addresses file)
```bash
EXP_CONFIG=configs/m2/A_balance_int1_rep1.yaml python src/runner.py
```

### 7.3 Summarize a single run log
```bash
python src/summarize.py logs/providerA_blocknumber_int1_rep1.jsonl
```

### 7.4 Run the full M2 matrix and generate a consolidated CSV summary
```bash
python src/batch_run.py "configs/m2/*.yaml" summary.csv
```

---

## 8. Configuration Examples

### 8.1 Blocknumber scenario (baseline, address-free)
```yaml
provider_id: providerA
chain_id: 11155111
rpc_url: "https://ethereum-sepolia-rpc.publicnode.com"
scenario: "blocknumber"
duration_s: 30
interval_s: 2
repeat_id: 1
out_log: "logs/providerA_blocknumber_int2_rep1.jsonl"
```

### 8.2 Balance scenario (address-bearing)
```yaml
provider_id: providerA
chain_id: 11155111
rpc_url: "https://ethereum-sepolia-rpc.publicnode.com"
scenario: "balance"
duration_s: 30
interval_s: 2
repeat_id: 1
addresses_file: "configs/addresses_demo.txt"
out_log: "logs/providerA_balance_int2_rep1.jsonl"
```

---

## 9. Notes on Data & Privacy
- Logs are designed to be analysis-friendly while minimizing sensitive payload storage. Prefer logging **derived indicators** (e.g., `has_address`, `params_hash`) rather than raw parameters when possible.
- Do not commit large raw logs to GitHub unless required. Prefer:
  - committing small, de-identified samples; or
  - committing screenshots / summary outputs as evidence.