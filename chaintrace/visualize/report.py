import networkx as nx
from pyvis.network import Network # type: ignore
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
        
        # Add physics controls (optimized for large graphs)
        net.set_options("""
        var options = {
          "physics": {
            "barnesHut": {
              "gravitationalConstant": -30000,
              "centralGravity": 0.3,
              "springLength": 95,
              "springConstant": 0.04,
              "damping": 0.09,
              "avoidOverlap": 0.1
            },
            "minVelocity": 0.75,
            "stabilization": {
                "enabled": true,
                "iterations": 1000,
                "updateInterval": 25,
                "onlyDynamicEdges": false,
                "fit": true
            }
          }
        }
        """)
        # net.show_buttons(filter_=['physics']) # Use custom options instead of default buttons
        
        # Save
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        net.save_graph(str(path))
        
        # Little hack to make it self-contained if needed, 
        # but PyVis usually links to CDN for vis.js. 
        # By default 'save_graph' creates a file that works offline if lib is present or online otherwise.
