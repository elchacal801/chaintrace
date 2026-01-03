import networkx as nx
from pyvis.network import Network
from pathlib import Path

class HTMLReportGenerator:
    def __init__(self, G: nx.DiGraph):
        self.G = G

    def generate(self, output_path: str, title: str = "Transaction Graph"):
        """
        Generate interactive HTML graph.
        """
        # Configure PyVis
        net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", notebook=False)
        
        # Convert NetworkX to PyVis
        # Note: PyVis handles this, but we want to ensure attributes are strings/numbers for JS
        net.from_nx(self.G)
        
        # Add physics controls
        net.show_buttons(filter_=['physics'])
        
        # Save
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        net.save_graph(str(path))
        
        # Little hack to make it self-contained if needed, 
        # but PyVis usually links to CDN for vis.js. 
        # By default 'save_graph' creates a file that works offline if lib is present or online otherwise.
