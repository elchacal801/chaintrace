import abc
import hashlib
import json
import time
from pathlib import Path
from typing import List, Optional, Any
from ..models import Transaction

class BaseCollector(abc.ABC):
    def __init__(self, chain: str, cache_dir: str = "data/raw/cache"):
        self.chain = chain
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> Path:
        """Generate a safe cache file path from a key."""
        hashed_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{self.chain}_{hashed_key}.json"

    def _read_cache(self, key: str, max_age_seconds: int = 86400) -> Optional[Any]:
        """Read from cache if exists and is fresh."""
        path = self._get_cache_path(key)
        if not path.exists():
            return None
        
        # Check specific modification time
        mtime = path.stat().st_mtime
        if time.time() - mtime > max_age_seconds:
            return None
            
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None

    def _write_cache(self, key: str, data: Any):
        """Write data to cache."""
        path = self._get_cache_path(key)
        with open(path, 'w') as f:
            json.dump(data, f)
            
    @abc.abstractmethod
    def fetch_transactions(self, address: str, start_block: int = 0) -> List[Transaction]:
        """Fetch transactions for an address."""
        pass
