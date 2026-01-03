from datetime import datetime
from chaintrace.models import Transaction

def test_transaction_decimals():
    # ETH (18 decimals)
    tx_eth = Transaction(
        chain="ethereum",
        tx_hash="0x123",
        block_number=1,
        timestamp=datetime.now(),
        from_address="0xA",
        to_address="0xB",
        value_wei=1000000000000000000, # 1 ETH
        decimals=18
    )
    assert tx_eth.get_value_human() == 1.0

    # BTC (8 decimals)
    tx_btc = Transaction(
        chain="bitcoin",
        tx_hash="abc",
        block_number=1,
        timestamp=datetime.now(),
        from_address="bc1a",
        to_address="bc1b",
        value_wei=100000000, # 1 BTC
        decimals=8
    )
    assert tx_btc.get_value_human() == 1.0

def test_transaction_addresses_lowercase():
    tx = Transaction(
        chain="test",
        tx_hash="0x123",
        block_number=1,
        timestamp=datetime.now(),
        from_address="0xABC", # Should convert to 0xabc
        to_address="0xDEF", # Should convert to 0xdef
        value_wei=0
    )
    assert tx.from_address == "0xabc"
    assert tx.to_address == "0xdef"
