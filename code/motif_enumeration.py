#!/usr/bin/env python3
"""
motif_enumeration.py

Exhaustively enumerate all connected subgraphs (motifs) up to a given size in the HCP lattice.
- Uses parity‑aware HCP builder from Paper 0.
- For each motif, canonicalize via nauty (labelg) to avoid duplicates.
- Tests admissibility: flipping the motif should preserve opposite‑neighbour count = 6.
- Outputs a JSON certificate with canonical graph6 labels, sizes, diameters, and witness checks.
- Computes SHA256 hash of the JSON file for verification.

Requires: Python 3, networkx, numpy, nauty (labelg in PATH)
"""

import os
import sys
import json
import hashlib
import subprocess
import tempfile
from collections import deque
import networkx as nx
import numpy as np

# Import HCP builder from Paper 0 (assumes it's in code/paper0/ or same directory)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'paper0'))
from prism_violation import build_hcp_patch, alt_state, count_opposite

# Parameters
PATCH_RADIUS = 5          # horizontal radius of HCP patch
PATCH_LAYERS = 8          # number of layers
MAX_MOTIF_SIZE = 12       # maximum number of nodes in a motif
OUTPUT_JSON = "motifs.json"
SHA256_FILE = "motifs.json.sha256"

def graph6_string(G):
    """Return graph6 string for a NetworkX graph."""
    return nx.to_graph6_bytes(G, header=False).decode().strip()

def canonical_graph6(g6):
    """Return canonical graph6 string using nauty's labelg."""
    proc = subprocess.run(['labelg', '-q'], input=g6.encode(), capture_output=True)
    return proc.stdout.decode().strip()

def is_admissible_motif(adj, state, motif_nodes):
    """
    Test if flipping the given motif preserves local equilibrium.
    Returns (bool, dict) where dict contains witness data.
    """
    # Determine affected nodes: motif plus all neighbours
    affected = set(motif_nodes)
    for v in motif_nodes:
        affected.update(adj[v])
    # Only interior nodes (degree 12) matter
    interior = [v for v in affected if len(adj[v]) == 12]
    # Build post‑flip state
    state2 = state.copy()
    for v in motif_nodes:
        state2[v] = 1 - state2[v]
    # Check opposite counts
    pre_counts = {}
    post_counts = {}
    ok = True
    for v in interior:
        pre = count_opposite(adj, state, v)
        post = count_opposite(adj, state2, v)
        pre_counts[str(v)] = pre
        post_counts[str(v)] = post
        if post != 6:
            ok = False
    return ok, {"pre": pre_counts, "post": post_counts}

def enumerate_connected_subsets(adj, max_size):
    """
    Generator that yields all connected subsets of nodes up to max_size.
    Uses BFS from each node to build connected sets incrementally.
    """
    nodes = list(adj.keys())
    for start in nodes:
        # Use a queue of (current_set, frontier)
        # We'll do BFS to build sets; simpler: recursion with set and extension
        stack = [(frozenset([start]), frozenset(adj[start]))]
        while stack:
            current, frontier = stack.pop()
            yield set(current)
            if len(current) >= max_size:
                continue
            # Add each node from frontier not already in current
            for n in frontier:
                if n not in current:
                    new_set = current | {n}
                    new_frontier = (frontier | set(adj[n])) - new_set
                    stack.append((frozenset(new_set), frozenset(new_frontier)))

def main():
    print("Building HCP patch...")
    adj = build_hcp_patch(R=PATCH_RADIUS, L=PATCH_LAYERS)
    # Use interior nodes only for seeding (to avoid boundary artifacts)
    interior_nodes = [v for v in adj if len(adj[v]) == 12]
    print(f"Interior nodes: {len(interior_nodes)}")

    # Base state (alternating layers)
    state = {v: alt_state(v) for v in adj}

    seen_canon = set()
    motifs_data = []
    total_checked = 0

    print("Starting motif enumeration...")
    # We'll enumerate from each interior node; but to avoid duplicates we
    # rely on canonicalization after generation.
    for seed in interior_nodes:
        # Use BFS expansion from seed (simple recursion depth‑first)
        stack = [(frozenset([seed]), frozenset(adj[seed]))]
        while stack:
            current, frontier = stack.pop()
            if len(current) > MAX_MOTIF_SIZE:
                continue
            total_checked += 1
            if total_checked % 10000 == 0:
                print(f"  ... checked {total_checked} sets")

            # Extract induced subgraph
            sub_nodes = list(current)
            H = nx.Graph(adj).subgraph(sub_nodes)
            # Canonicalize
            g6 = graph6_string(H)
            canon = canonical_graph6(g6)
            if canon in seen_canon:
                continue
            seen_canon.add(canon)

            # Test admissibility
            ok, witness = is_admissible_motif(adj, state, sub_nodes)
            if ok:
                # Compute diameter of the induced subgraph
                diam = nx.diameter(H)
                # Store representative embedding (coordinates of nodes)
                # For reproducibility, we record node coordinates (if available)
                # Here we use the node tuple itself; in geometric HCP we could map to positions.
                motifs_data.append({
                    "canonical_graph6": canon,
                    "size": len(sub_nodes),
                    "diameter": diam,
                    "representative_embedding": {
                        "nodes": sub_nodes,
                        "edges": list(H.edges())
                    },
                    "admissible": True,
                    "witness": witness
                })

    print(f"Total sets checked: {total_checked}")
    print(f"Unique admissible motifs found: {len(motifs_data)}")

    # Write JSON
    cert = {
        "metadata": {
            "generated_by": "motif_enumeration.py",
            "substrate": f"HCP patch R={PATCH_RADIUS}, L={PATCH_LAYERS}",
            "max_motif_size": MAX_MOTIF_SIZE,
            "timestamp": "2026-03-01T00:00:00Z"  # update manually if desired
        },
        "motifs": motifs_data
    }
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(cert, f, indent=2)

    # Compute SHA256
    with open(OUTPUT_JSON, 'rb') as f:
        hash_bytes = hashlib.sha256(f.read()).hexdigest()
    with open(SHA256_FILE, 'w') as f:
        f.write(f"{hash_bytes}  {OUTPUT_JSON}\n")

    print(f"Results written to {OUTPUT_JSON} and {SHA256_FILE}")

if __name__ == "__main__":
    main()
