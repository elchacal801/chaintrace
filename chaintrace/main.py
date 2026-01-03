import typer
import os
import json
from rich.console import Console
from dotenv import load_dotenv

# Components
from .collectors.etherscan import EtherscanCollector
from .graph.builder import GraphBuilder
from .analysis.heuristics import tag_nodes
from .visualize.report import HTMLReportGenerator

# Load env
load_dotenv()

app = typer.Typer(help="ChainTrace: Crypto forensics toolkit.")
console = Console()

@app.command()
def analyze(
    address: str = typer.Option(..., help="Target address to analyze"),
    chain: str = typer.Option("ethereum", help="Blockchain network (ethereum, arbitrum)"),
    depth: int = typer.Option(1, help="Hop depth for tracing"),
    output_dir: str = typer.Option("data/outputs", help="Directory for results")
):
    """
    Analyze a specific address, build interaction graph, and generate report.
    """
    console.print(f"[bold green]Starting analysis for {address} on {chain} (depth={depth})[/bold green]")
    
    from .collectors.bitcoin import BitcoinCollector

    if chain.lower() == "bitcoin":
        collector = BitcoinCollector()
    else:
        # Default to Etherscan / Ethereum
        api_key = os.getenv("ETHERSCAN_API_KEY")
        if not api_key:
            console.print("[bold red]ERROR: ETHERSCAN_API_KEY not found in .env[/bold red]")
            raise typer.Exit(code=1)
        collector = EtherscanCollector(api_key=api_key, chain=chain)
    
    # 1. Fetch
    console.print("[yellow]Step 1: Fetching transactions...[/yellow]")
    # For MVP, we only do depth 1 (fetch target's txs). 
    # Real depth > 1 requires recursive fetching.
    txs = collector.fetch_transactions(address)
    console.print(f"  Fetched {len(txs)} transactions.")
    
    if not txs:
        console.print("[red]No transactions found. Exiting.[/red]")
        raise typer.Exit()
    
    # 2. Build Graph
    console.print("[yellow]Step 2: Building graph...[/yellow]")
    builder = GraphBuilder(txs)
    G = builder.build()
    console.print(f"  Graph created: {len(G.nodes)} nodes, {len(G.edges)} edges.")
    
    # 3. Analytics
    console.print("[yellow]Step 3: Finding patterns...[/yellow]")
    tag_nodes(G)
    
    # 4. Outputs
    console.print("[yellow]Step 4: Generating outputs...[/yellow]")
    
    # CSV
    df = builder.get_edges_dataframe()
    csv_path = f"{output_dir}/edges_{address}.csv"
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(csv_path, index=False)
    console.print(f"  Examples saved to {csv_path}")
    
    # Summary JSON (Simple Top 5 for now)
    summary = {
        "target": address,
        "total_txs": len(txs),
        "total_volume_eth": sum(t.get_value_human() for t in txs),
        "top_nodes": [n for n in G.nodes if G.degree(n) > 5]
    }
    json_path = f"{output_dir}/summary_{address}.json"
    with open(json_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # HTML Report
    viz_path = f"{output_dir}/report_{address}.html"
    viz = HTMLReportGenerator(G)
    viz.generate(viz_path)
    
    console.print(f"[bold blue]Done! Open {viz_path} to view the graph.[/bold blue]")

@app.command()
def fetch(
    address: str = typer.Option(..., help="Target address"),
):
    """
    Just fetch raw data for an address.
    """
    api_key = os.getenv("ETHERSCAN_API_KEY")
    if not api_key:
        print("Error: No API Key")
        return
        
    collector = EtherscanCollector(api_key=api_key)
    txs = collector.fetch_transactions(address)
    print(f"Fetched {len(txs)} transactions for {address}")

if __name__ == "__main__":
    app()
