import networkx as nx
import math
import pandas as pd
from typing import List, Dict
from ..models import Transaction

class GraphBuilder:
    def __init__(self, transactions: List[Transaction]):
        self.raw_txs = transactions
        self.G: nx.DiGraph = nx.DiGraph()
        
    def build(self) -> nx.DiGraph:
        """
        Convert transactions to a directed graph.
        Aggregates multiple txs between same pair into one weighted edge.
        """
        self.G.clear()
        
        edge_buffer: Dict[tuple, Dict] = {}
        
        for tx in self.raw_txs:
            if tx.is_error:
                continue
                
            src = tx.from_address
            dst = tx.to_address
            
            # Handle contract creation (dst=None)
            if not dst:
                dst = "CONTRACT_CREATION" 
            
            key = (src, dst)
            
            if key not in edge_buffer:
                edge_buffer[key] = {
                    "count": 0,
                    "value_wei": 0,
                    "first_seen": tx.timestamp,
                    "last_seen": tx.timestamp,
                    "tx_hashes": []
                }
            
            meta = edge_buffer[key]
            meta["count"] += 1
            meta["value_wei"] += tx.value_wei
            meta["first_seen"] = min(meta["first_seen"], tx.timestamp)
            meta["last_seen"] = max(meta["last_seen"], tx.timestamp)
            # Store first 5 hashes to avoid bloat
            if len(meta["tx_hashes"]) < 5:
                meta["tx_hashes"].append(tx.tx_hash)
        
        # Determine decimals/symbol from first tx (assumption: homogenous chain)
        decimals = 18
        symbol = "ETH"
        if self.raw_txs:
            decimals = self.raw_txs[0].decimals
            symbol = self.raw_txs[0].token_symbol or "Units"

        divider = 10 ** decimals

        # Add to graph
        for (src, dst), meta in edge_buffer.items():
            human_val = meta["value_wei"] / divider
            
            # Log scaling for visual width (1 to 10 pixels range)
            width = 1
            if human_val > 0:
                width = min(1 + math.log(human_val + 1), 10)

            self.G.add_edge(
                src, 
                dst, 
                weight=width,              # Use scaled width for physics to avoid 10^18 force explosion
                width=width,               # Visual width
                count=meta["count"],
                value_human=human_val,
                first_seen=meta["first_seen"].isoformat(),
                last_seen=meta["last_seen"].isoformat(),
                last_seen=meta["last_seen"].isoformat(),
                label=f"{human_val:.4f} {symbol}",
                title=f"Transfers: {meta['count']}<br>Vol: {human_val:.4f} {symbol}"
            )
            
            # Update node degrees/attrs if needed (can be done later)
            self.G.nodes[src]["type"] = "address"
            self.G.nodes[dst]["type"] = "address"

        return self.G

    def get_edges_dataframe(self) -> pd.DataFrame:
        """Export edges to Pandas for CSV."""
        return nx.to_pandas_edgelist(self.G)
