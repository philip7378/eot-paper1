#!/usr/bin/env python3
"""
fig1_conceptual.py

Draw a conceptual directed graph representing configurations,
admissible subset, and an infinite path.
"""

import matplotlib.pyplot as plt
import networkx as nx

def main():
    G = nx.DiGraph()
    # Create a small DAG with branching and merging
    edges = [
        (0,1), (0,2), (1,3), (1,4), (2,5), (2,6),
        (3,7), (4,7), (5,8), (6,8), (7,9), (8,9),
        (9,10), (10,11), (11,12), (12,13), (13,14), (14,0)  # cycle to show infinite path
    ]
    G.add_edges_from(edges)
    pos = nx.spring_layout(G, seed=42)  # positions for all nodes

    # Nodes
    admissible = list(range(15))  # all nodes admissible for simplicity
    path_nodes = [0,1,3,7,9,10,11,12,13,14,0]  # infinite path (cycle)
    path_edges = list(zip(path_nodes, path_nodes[1:]))

    plt.figure(figsize=(8,8))
    nx.draw_networkx_nodes(G, pos, nodelist=admissible, node_color='lightblue', node_size=500)
    nx.draw_networkx_nodes(G, pos, nodelist=path_nodes, node_color='red', node_size=600)
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), arrowstyle='->', arrowsize=20,
                           edge_color='gray', width=1.5)
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, arrowstyle='->', arrowsize=20,
                           edge_color='red', width=3)
    nx.draw_networkx_labels(G, pos, font_size=10, font_color='black')

    plt.title("Figure 1: Conceptual structure of EOT\n(Red: infinite realization)")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('fig1_conceptual.pdf')
    plt.savefig('fig1_conceptual.png')
    print("Saved fig1_conceptual.pdf")

if __name__ == "__main__":
    main()
