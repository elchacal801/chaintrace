import os
from dotenv import load_dotenv
from chaintrace.collectors.etherscan import EtherscanCollector

# Load env from .env file
load_dotenv()

def test_fetch():
    api_key = os.getenv("ETHERSCAN_API_KEY")
    if not api_key:
        print("SKIP: No ETHERSCAN_API_KEY found in .env")
        return

    # Use a known address: Vitalik's wallet
    target = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    
    print(f"Testing fetch for {target}...")
    collector = EtherscanCollector(api_key=api_key)
    
    # Fetch
    txs = collector.fetch_transactions(target)
    
    print(f"Fetched {len(txs)} transactions.")
    if len(txs) > 0:
        print("First TX Sample:")
        t = txs[0]
        print(f"  Hash: {t.tx_hash}")
        print(f"  Value: {t.get_value_human()} units")
        print(f"  From: {t.from_address}")
        print(f"  To: {t.to_address}")
        print(f"  Date: {t.timestamp}")

if __name__ == "__main__":
    test_fetch()
