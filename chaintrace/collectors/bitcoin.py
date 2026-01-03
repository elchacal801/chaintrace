import requests
import time
from datetime import datetime
from typing import List
from ..models import Transaction
from .base import BaseCollector

class BitcoinCollector(BaseCollector):
    BASE_URL = "https://mempool.space/api"
    
    def __init__(self, chain: str = "bitcoin", cache_dir: str = "data/raw/cache"):
        super().__init__(chain, cache_dir)
        self.last_call = 0
        self.rate_limit_delay = 0.5  # Respect mempool.space public limits

    def _rate_limit(self):
        now = time.time()
        elapsed = now - self.last_call
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_call = time.time()

    def fetch_transactions(self, address: str, start_block: int = 0) -> List[Transaction]:
        """
        Fetch TXs from Mempool.space.
        Address -> /address/:address/txs (returns last 50).
        For full history we'd need to chain /txs/chain/:last_txid.
        MVP: Fetch last 50-100 txs.
        """
        # 1. Check Cache
        cache_key = f"{address}_btc_recent"
        cached_data = self._read_cache(cache_key)
        
        raw_txs = []
        if cached_data:
            print(f"DEBUG: Loaded {len(cached_data)} BTC tx batches from cache")
            raw_txs = cached_data
        else:
            self._rate_limit()
            url = f"{self.BASE_URL}/address/{address}/txs"
            try:
                print(f"DEBUG: Requesting {url}")
                resp = requests.get(url, timeout=15)
                resp.raise_for_status()
                raw_txs = resp.json()
                self._write_cache(cache_key, raw_txs)
            except Exception as e:
                print(f"ERROR: BTC Fetch failed: {e}")
                return []

        # 2. Normalize
        normalized = []
        for tx in raw_txs:
            try:
                txid = tx["txid"]
                block_height = tx["status"].get("block_height", 0)
                ts = tx["status"].get("block_time", int(time.time()))
                dt = datetime.fromtimestamp(ts)
                
                # Heuristic: Sender is the address of the first input
                # (Assumes common ownership of inputs)
                sender = None
                if tx["vin"]:
                    prevout = tx["vin"][0].get("prevout")
                    if prevout:
                        sender = prevout.get("scriptpubkey_address")
                    else:
                        sender = "COINBASE" # Coinbase tx
                
                if not sender:
                    sender = "UNKNOWN"

                # Expand outputs into transactions
                for vout in tx["vout"]:
                    recipient = vout.get("scriptpubkey_address")
                    value = vout.get("value", 0)
                    
                    if not recipient:
                        continue # OP_RETURN or similar
                        
                    normalized.append(Transaction(
                        chain="bitcoin",
                        tx_hash=txid,
                        block_number=block_height,
                        timestamp=dt,
                        from_address=sender,
                        to_address=recipient,
                        value_wei=int(value),
                        decimals=8,
                        token_symbol="BTC",
                        gas_used=tx["fee"],
                        gas_price=0
                    ))
            except Exception as e:
                print(f"WARNING: Failed to parse BTC tx {tx.get('txid')}: {e}")
                continue
                
        return normalized
