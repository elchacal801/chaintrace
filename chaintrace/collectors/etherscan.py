import requests
import time
from datetime import datetime
from typing import List
from ..models import Transaction
from .base import BaseCollector

class EtherscanCollector(BaseCollector):
    BASE_URL = "https://api.etherscan.io/v2/api"
    
    def __init__(self, api_key: str, chain: str = "ethereum", cache_dir: str = "data/raw/cache"):
        super().__init__(chain, cache_dir)
        self.api_key = api_key
        self.last_call = 0
        self.rate_limit_delay = 0.25  # 4 calls/sec (Free tier 5/sec)

    def _rate_limit(self):
        now = time.time()
        elapsed = now - self.last_call
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_call = time.time()

    def fetch_transactions(self, address: str, start_block: int = 0) -> List[Transaction]:
        """
        Fetch 'Normal' transactions using V2 API.
        """
        # 1. Try Cache first
        cache_key = f"{address}_normal_{start_block}"
        cached_data = self._read_cache(cache_key)
        
        raw_txs = []
        if cached_data:
            print(f"DEBUG: Loaded {len(cached_data)} txs from cache")
            raw_txs = cached_data
        else:
            # 2. Fetch from API
            self._rate_limit()
            params = {
                "chainid": "1",  # Ethereum Mainnet
                "module": "account",
                "action": "txlist",
                "address": address,
                "startblock": start_block,
                "endblock": 99999999,
                "sort": "asc",
                "apikey": self.api_key
            }
            try:
                resp = requests.get(self.BASE_URL, params=params, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                
                if data["status"] == "1" and data["message"] == "OK":
                    raw_txs = data["result"]
                    # Write to cache
                    self._write_cache(cache_key, raw_txs)
                elif data["message"] == "No transactions found":
                    raw_txs = []
                else:
                    print(f"ERROR: Etherscan API error: {data['message']}")
                    print(f"Full response: {data}")
                    return []
            except Exception as e:
                print(f"ERROR: HTTP Request failed: {e}")
                return []

        # 3. Normalize
        normalized = []
        for tx in raw_txs:
            try:
                # Etherscan returns timestamps as strings
                ts = int(tx["timeStamp"])
                dt = datetime.fromtimestamp(ts)
                
                normalized.append(Transaction(
                    chain=self.chain,
                    tx_hash=tx["hash"],
                    block_number=int(tx["blockNumber"]),
                    timestamp=dt,
                    from_address=tx["from"],
                    to_address=tx["to"] if tx["to"] else None, # Empty string means contract creation usually
                    value_wei=int(tx["value"]),
                    gas_used=int(tx["gasUsed"]),
                    gas_price=int(tx["gasPrice"]),
                    is_error=tx.get("isError") == "1",
                    is_internal=False
                ))
            except Exception as e:
                print(f"WARNING: Failed to parse tx {tx.get('hash')}: {e}")
                continue
                
        return normalized
