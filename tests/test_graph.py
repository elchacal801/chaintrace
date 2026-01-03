from datetime import datetime
from chaintrace.models import Transaction
from chaintrace.graph.builder import GraphBuilder

def test_graph_aggregation():
    # Two txs from A -> B
    tx1 = Transaction(
        chain="eth", tx_hash="1", block_number=1, timestamp=datetime.now(),
        from_address="0xa", to_address="0xb", value_wei=10**18, decimals=18
    )
    tx2 = Transaction(
        chain="eth", tx_hash="2", block_number=2, timestamp=datetime.now(),
        from_address="0xa", to_address="0xb", value_wei=2 * 10**18, decimals=18
    )
    
    # One tx from B -> A
    tx3 = Transaction(
        chain="eth", tx_hash="3", block_number=3, timestamp=datetime.now(),
        from_address="0xb", to_address="0xa", value_wei=10**18, decimals=18
    )
    
    builder = GraphBuilder([tx1, tx2, tx3])
    G = builder.build()
    
    # Check Edge A->B
    edge_ab = G.get_edge_data("0xa", "0xb")
    assert edge_ab is not None
    assert edge_ab["count"] == 2
    assert edge_ab["value_human"] == 3.0 # 1 + 2
    
    # Check Edge B->A
    edge_ba = G.get_edge_data("0xb", "0xa")
    assert edge_ba is not None
    assert edge_ba["count"] == 1
    assert edge_ba["value_human"] == 1.0

def test_contract_creation():
    tx = Transaction(
        chain="eth", tx_hash="1", block_number=1, timestamp=datetime.now(),
        from_address="0xa", to_address=None, value_wei=0
    )
    builder = GraphBuilder([tx])
    G = builder.build()
    
    assert G.has_edge("0xa", "CONTRACT_CREATION")
