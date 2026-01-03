import networkx as nx
from typing import Dict, List

def detect_patterns(G: nx.DiGraph) -> Dict[str, List[str]]:
    """
    Identify nodes matching specific structural patterns.
    """
    patterns: Dict[str, List[str]] = {
        "fan_out": [],
        "fan_in": [],
        "bridge/mixer": []
    }
    
    if len(G.nodes) == 0:
        return patterns

    for node in G.nodes():
        in_degree = G.in_degree(node)
        out_degree = G.out_degree(node)
        
        # Heuristic: Fan Out (Dispenser/Exchange user withdrawal)
        if out_degree > 5 and in_degree <= 2:
            patterns["fan_out"].append(node)
            
        # Heuristic: Fan In (Collector/Exchange deposit address)
        if in_degree > 5 and out_degree <= 2:
            patterns["fan_in"].append(node)
            
        # Heuristic: High density pass-through (Bridge/Mixer)
        if in_degree > 10 and out_degree > 10:
            patterns["bridge/mixer"].append(node)
            
    return patterns

def tag_nodes(G: nx.DiGraph):
    """
    Apply risk tags to nodes in the graph.
    """
    patterns = detect_patterns(G)
    
    for node in patterns["fan_out"]:
        G.nodes[node]["tag"] = "Dispenser"
        G.nodes[node]["color"] = "#FF9900" # Orange
        
    for node in patterns["fan_in"]:
        G.nodes[node]["tag"] = "Collector"
        G.nodes[node]["color"] = "#00CCFF" # Blue
        
    for node in patterns["bridge/mixer"]:
        G.nodes[node]["tag"] = "High Activity"
        G.nodes[node]["color"] = "#FF0000" # Red
