from typing import List, Tuple, Any

def scenario_blocknumber() -> List[Tuple[str, Any]]:
    return [("eth_blockNumber", [])]

def scenario_balance(addresses: List[str]) -> List[Tuple[str, Any]]:
    # latest block
    return [("eth_getBalance", [addr, "latest"]) for addr in addresses]

def scenario_nonce(addresses: List[str]) -> List[Tuple[str, Any]]:
    return [("eth_getTransactionCount", [addr, "latest"]) for addr in addresses]

def scenario_call_example() -> List[Tuple[str, Any]]:
    # Minimal eth_call to a fixed address with empty data (example). You can replace later.
    # This is just to exercise eth_call path without building DeFi logic.
    call_obj = {"to": "0x0000000000000000000000000000000000000000", "data": "0x"}
    return [("eth_call", [call_obj, "latest"])]
