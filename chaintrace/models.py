from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional

class Transaction(BaseModel):
    """
    Normalized transaction model independent of the specific chain data source.
    """
    chain: str = Field(..., description="Chain name (ethereum, arbitrum)")
    tx_hash: str = Field(..., description="Transaction hash")
    block_number: int
    timestamp: datetime
    
    from_address: Optional[str]  # None for coinbase/mint
    to_address: Optional[str]
    value_wei: int = Field(..., description="Value in smallest unit (Wei/Sats)")
    decimals: int = 18 # Default Ethereum
    gas_used: int = 0
    gas_price: int = 0
    
    is_error: bool = False
    is_internal: bool = False 
    
    # Enrichment fields
    token_symbol: Optional[str] = "ETH"
    token_value: Optional[float] = None
    
    @field_validator('from_address', 'to_address', mode='before')
    def lower_case_addresses(cls, v):
        return v.lower() if v else None

    def get_value_human(self) -> float:
        return self.value_wei / (10 ** self.decimals)
