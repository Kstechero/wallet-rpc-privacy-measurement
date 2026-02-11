# Wallet–RPC Privacy Leakage Measurement (Empirical Study)

## 1. Background
In Ethereum and other EVM ecosystems, user wallets (e.g., MetaMask) typically do not maintain a full node locally. Instead, they rely on third-party or public RPC (JSON-RPC) endpoints to read on-chain data, simulate contract calls, and broadcast transactions.  
This creates potential privacy risks: RPC providers (and observers along the network path) may profile user behavior based on request metadata and semantics (e.g., method type, timestamps, request frequency, whether address parameters appear), and may even attempt multi-address linkage (linkability) inference.

The goal of this project is to conduct an **empirical measurement** of these risks: by running the same controlled workloads across different RPC providers, collecting structured logs, and computing metrics to support evidence-based conclusions.

---

## 2. Problem Statement
This project aims to measure and quantify the types and degree of privacy information that may be leaked through wallet RPC requests, and to compare different RPC providers along these dimensions:
- **Availability:** success rate, timeout rate, error types
- **Performance:** latency distribution (median / average / max, etc.)
- **Privacy exposure proxies:**
  - method distribution (what actions the user is performing)
  - presence of address-bearing requests (`has_address`)
  - request cadence/frequency (behavioral signatures)

---

## 3. Scope
For **Milestone 1**, the scope focuses on:
- **Network:** Sepolia testnet (`chain_id = 11155111`)
- **Scenarios:**
  - `blocknumber`: calls `eth_blockNumber` (no address parameter; connectivity/performance baseline)
  - `balance`: calls `eth_getBalance` (includes address parameter; address exposure proxy)
- **Comparison targets:** at least two different RPC endpoints (providerA/providerB)
- **Data output:** JSONL (one JSON record per RPC request)

Out of scope for Milestone 1 (possible later extensions):
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
- automatically issues JSON-RPC requests (e.g., `eth_blockNumber`, `eth_getBalance`)
- logs key per-request metadata into JSONL
- runs identical workloads across providers for A/B comparison
- summarizes logs via `summarize.py`

In one sentence: the harness is an automated framework that enables repeatable experiments and produces analyzable outputs.

---

## 6. Project Structure
- `configs/`
  - `exp_sepolia_providerA.yaml`: Provider-A experiment config
  - `exp_sepolia_providerB.yaml`: Provider-B experiment config
  - `addresses_demo.txt`: address list for balance queries (one `0x...` per line)
- `src/`
  - `runner.py`: entry point; loads config, runs scenarios, writes logs
  - `rpc_client.py`: JSON-RPC client (HTTP)
  - `scenarios.py`: scenario definitions and parameter construction
  - `logger.py`: constructs and appends JSONL records
  - `summarize.py`: summarizes logs into metrics
- `logs/`
  - runtime-generated JSONL logs (recommended to ignore or only commit de-identified samples)

---

## 7. Configuration Examples
### 7.1 Blocknumber scenario (baseline)
```yaml
provider_id: providerA
chain_id: 11155111
rpc_url: "https://ethereum-sepolia-rpc.publicnode.com"
scenario: "blocknumber"
duration_s: 30
interval_s: 2
out_log: "logs/run_providerA.jsonl"
