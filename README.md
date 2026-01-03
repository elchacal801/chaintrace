# ChainTrace

**Professional Crypto Forensics & Visualization Toolkit for CTI Analysts.**

ChainTrace is a practitioner-focused tool designed to instantly triage cryptocurrency addresses, map their interaction networks, and identify common laundering patterns (peeling, fan-out, mixing) without requiring expensive commercial licenses. It supports **Ethereum** and **Bitcoin** (via public APIs).

## Key Features

- **Multi-Chain Support**: seamlessly trace ETH (Etherscan) and BTC (Mempool.space).
- **Zero-Infrastructure**: Runs entirely on public APIs. No local node required.
- **Graph Intelligence**: Automatically builds directed graphs detecting "Fan-Out" (Dispenser) and "Fan-In" (Aggregator) patterns.
- **Analyst-Ready Outputs**:
    - `report.html`: Interactive, self-contained visualization file.
    - `edges.csv`: Clean edge list for import into Gephi, Maltego, or Neo4j.

## Quickstart

### Installation

```bash
# Clone and install dependencies
git clone https://github.com/your-org/chaintrace.git
cd chaintrace
pip install -r requirements.txt

# Configure API Keys
cp .env.example .env
# Edit .env to add ETHERSCAN_API_KEY (Bitcoin does not require a key)
```

### Usage

**1. Trace an Ethereum Address**
```bash
python -m chaintrace.main analyze --address 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 --chain ethereum
```

**2. Trace a Bitcoin Address**
```bash
# Example: Silk Road Seized Funds
python -m chaintrace.main analyze --address 1HQ3Go3ggs8pFnXuHVHRytPCq5fGG8Hbhx --chain bitcoin
```

**3. View Results**
Open the generated HTML file in your browser:
- `data/outputs/report_[address].html`

## Practitioner Use Cases

### 1. Ransomware Triage
**Scenario**: A victim reports a Bitcoin ransom payment address.
**Action**: Run `chaintrace analyze`.
**Insight**: 
- If the graph shows immediate "Fan-In" to a known exchange hot wallet, law enforcement subpoena is viable.
- If it shows a "Peel Chain" (small amounts peeled off while large change moves forward), the actor is likely laundering manually.

### 2. Fraud Investigation
**Scenario**: "Pig Butchering" scam destination wallet.
**Action**: Trace headers.
**Insight**: Identify if the wallet is a "Collector" node (aggregating from many victims) or a "Mule" node (cashing out).

## Detection Logic & Heuristics

The tool applies the following tags to nodes in the graph:

| Pattern | Tag | Color | Interpretation |
| :--- | :--- | :--- | :--- |
| **Fan-Out** | Dispenser | Orange | Sends to many (>5) unique addresses. Typical of Exchanges (Withdrawal), Faucets, or Payroll. |
| **Fan-In** | Collector | Blue | Receives from many (>5) unique addresses. Typical of Exchanges (Deposit), ICOs, or C2 Infrastructure. |
| **High Activity** | High Activity | Red | Very high degree (>10 in/out). Likely a Bridge, Mixer, or Exchange Hot Wallet. |

## Automation & CI

This repo includes GitHub Actions to ensure code quality:
- **Linting**: Ruff
- **Type Checking**: Mypy
- **Tests**: Pytest (Unit & Integration)

## Ethics & OPSEC

> [!WARNING]
> **OPSEC Notice**: This tool queries **public APIs** (Etherscan, Mempool.space).
> - The API provider **can see** which addresses you are investigating.
> - Do **not** use this tool for TLP:RED investigations where the *interest* in an address is itself sensitive.
> - For high-security cases, fork this tool to use a local node collector (planned v2).

## License

MIT
