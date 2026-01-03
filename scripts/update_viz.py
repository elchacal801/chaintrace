import os
import sys
import argparse
from typing import List, Dict
from chaintrace.collectors.etherscan import EtherscanCollector
from chaintrace.collectors.bitcoin import BitcoinCollector
from chaintrace.graph.builder import GraphBuilder
from chaintrace.analysis.heuristics import tag_nodes
from chaintrace.visualize.report import HTMLReportGenerator
from chaintrace.models import Transaction

# Directories
OUTPUT_DIR = "docs" # GitHub Pages publishes from docs/ or gh-pages branch. docs/ is easier for main branch.
DATA_DIR = "data/outputs"

# Target List
TARGETS = [
    {"name": "Vitalik Buterin", "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045", "chain": "ethereum"},
    {"name": "Mark Cuban", "address": "0xa679c6154b8d4619af9f83f0bf9a13a680e01ecf", "chain": "ethereum"},
    {"name": "Justin Sun", "address": "0x3ddfa8ec3052539b6b95494129381e964523a0d3", "chain": "ethereum"},
    {"name": "Silk Road Seized (US Govt)", "address": "1HQ3Go3ggs8pFnXuHVHRytPCq5fGG8Hbhx", "chain": "bitcoin"},
]

def main():
    print("Starting Daily Visualization Update...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

    etherscan_key = os.getenv("ETHERSCAN_API_KEY")
    if not etherscan_key:
        print("WARNING: ETHERSCAN_API_KEY not found. Skipping ETH targets.")

    # We will generate individual reports and a main index.html
    reports = []

    for t in TARGETS:
        print(f"Processing {t['name']} ({t['chain']})...")
        
        try:
            # 1. Collector
            collector = None
            if t["chain"] == "ethereum":
                if etherscan_key:
                   collector = EtherscanCollector(api_key=etherscan_key)
            elif t["chain"] == "bitcoin":
                collector = BitcoinCollector()
            
            if not collector:
                print(f"Skipping {t['name']} (No collector available)")
                continue

            # 2. Fetch
            txs = collector.fetch_transactions(t["address"])
            if not txs:
                print(f"No txs found for {t['name']}")
                continue
            
            # 3. Build Graph
            builder = GraphBuilder(txs)
            G = builder.build()
            tag_nodes(G)
            
            # 4. Generate Report
            # Clean filename
            safe_name = t['name'].lower().replace(" ", "_").replace("(", "").replace(")", "")
            filename = f"report_{safe_name}.html"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            viz = HTMLReportGenerator(G)
            viz.generate(filepath)
            
            reports.append({
                "name": t['name'],
                "chain": t['chain'],
                "address": t['address'],
                "file": filename,
                "nodes": len(G.nodes),
                "edges": len(G.edges)
            })
            print(f"Generated {filepath}")

        except Exception as e:
            print(f"Error processing {t['name']}: {e}")

    # 5. Generate Index Page (Dashboard)
    index_path = os.path.join(OUTPUT_DIR, "index.html")
    with open(index_path, "w") as f:
        f.write(generate_index_html(reports))
    print(f"Dashboard updated at {index_path}")

def generate_index_html(reports: List[Dict]) -> str:
    rows = ""
    for r in reports:
        rows += f"""
        <tr>
            <td>{r['name']}</td>
            <td><span class="badge {r['chain']}">{r['chain'].upper()}</span></td>
            <td><code>{r['address'][:10]}...</code></td>
            <td>{r['nodes']} / {r['edges']}</td>
            <td><a href="{r['file']}" class="btn">View Graph</a></td>
        </tr>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ChainTrace Intelligence Dashboard</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #0f111a; color: #eaeaeb; }}
            h1 {{ border-bottom: 2px solid #30363d; padding-bottom: 10px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background: #161b22; border-radius: 6px; overflow: hidden; }}
            th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #30363d; }}
            th {{ background: #21262d; color: #8b949e; font-weight: 600; text-transform: uppercase; font-size: 0.85em; }}
            tr:hover {{ background: #1f2428; }}
            code {{ font-family: "SF Mono", Monaco, Consolas, monospace; background: rgba(110,118,129,0.4); padding: 2px 4px; border-radius: 3px; font-size: 0.9em; }}
            .btn {{ display: inline-block; padding: 6px 12px; font-size: 14px; font-weight: 500; color: #ffffff; background-color: #238636; border: 1px solid rgba(240,246,252,0.1); border-radius: 6px; text-decoration: none; }}
            .btn:hover {{ background-color: #2ea043; }}
            .badge {{ display: inline-block; padding: 2px 7px; font-size: 12px; font-weight: 500; border-radius: 2em; border: 1px solid rgba(240,246,252,0.1); }}
            .badge.ethereum {{ background: #3c3c3d; color: #a29bfe; }}
            .badge.bitcoin {{ background: #3c3c3d; color: #fab1a0; }}
            footer {{ margin-top: 40px; color: #8b949e; font-size: 0.9em; text-align: center; }}
        </style>
    </head>
    <body>
        <h1>⛓️ ChainTrace Intelligence Dashboard</h1>
        <p>Real-time tracked high-profile entities. Graphs updated automatically via GitHub Actions.</p>
        
        <table>
            <thead>
                <tr>
                    <th>Target Entity</th>
                    <th>Network</th>
                    <th>Address</th>
                    <th>Graph Size (N/E)</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        
        <footer>Generated by ChainTrace Engine • Last Update: {os.popen('date').read().strip() if sys.platform != 'win32' else 'Now'}</footer>
    </body>
    </html>
    """

if __name__ == "__main__":
    main()
