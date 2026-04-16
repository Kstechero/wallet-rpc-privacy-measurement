from typing import Any, List, Tuple


def scenario_blocknumber() -> List[Tuple[str, Any]]:
    return [("eth_blockNumber", [])]


def scenario_balance(addresses: List[str]) -> List[Tuple[str, Any]]:
    return [("eth_getBalance", [addr, "latest"]) for addr in addresses]


def scenario_nonce(addresses: List[str]) -> List[Tuple[str, Any]]:
    return [("eth_getTransactionCount", [addr, "latest"]) for addr in addresses]


def scenario_call_example() -> List[Tuple[str, Any]]:
    """
    Minimal eth_call to exercise contract-call path without depending on
    a live DeFi/NFT app. 'to' is set to zero-address for a lightweight control.
    """
    call_obj = {"to": "0x0000000000000000000000000000000000000000", "data": "0x"}
    return [("eth_call", [call_obj, "latest"])]


def scenario_estimate_gas(addresses: List[str]) -> List[Tuple[str, Any]]:
    """
    Minimal estimateGas to simulate a wallet pre-flight request.
    Uses the first address as 'from' if available.
    """
    from_addr = addresses[0] if addresses else "0x0000000000000000000000000000000000000000"
    tx_obj = {
        "from": from_addr,
        "to": "0x0000000000000000000000000000000000000000",
        "value": "0x0",
        "data": "0x",
    }
    return [("eth_estimateGas", [tx_obj])]


def scenario_wallet_refresh(addresses: List[str]) -> List[Tuple[str, Any]]:
    """
    A lightweight multi-step wallet refresh workflow:
      - latest block
      - account balance
      - account nonce
      - estimate gas
    This is closer to realistic wallet behavior than a single-method scenario.
    """
    addr = addresses[0] if addresses else "0x0000000000000000000000000000000000000000"
    tx_obj = {
        "from": addr,
        "to": "0x0000000000000000000000000000000000000000",
        "value": "0x0",
        "data": "0x",
    }
    return [
        ("eth_blockNumber", []),
        ("eth_getBalance", [addr, "latest"]),
        ("eth_getTransactionCount", [addr, "latest"]),
        ("eth_estimateGas", [tx_obj]),
    ]