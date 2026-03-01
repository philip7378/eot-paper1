#!/usr/bin/env python3
"""
growth_measurement.py

Measure the growth function |B_r(v)| for the HCP lattice and fit the exponent d.
Uses a large patch, samples interior nodes, and computes distances.
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'paper0'))
from prism_violation import build_hcp_patch

def bfs_distances(adj, source, max_dist):
    """Return dictionary of distances from source up to max_dist."""
    visited = {source: 0}
    q = deque([source])
    while q:
        v = q.popleft()
        d = visited[v]
        if d >= max_dist:
            continue
        for nb in adj[v]:
            if nb not in visited:
                visited[nb] = d+1
                q.append(nb)
    return visited

def main():
    # Build a large patch
    R = 20
    L = 20
    print(f"Building HCP patch with R={R}, L={L}...")
    adj = build_hcp_patch(R, L)
    interior = [v for v in adj if len(adj[v]) == 12]
    print(f"Interior nodes: {len(interior)}")

    # Sample a subset of interior nodes
    sample_size = min(100, len(interior))
    sample = np.random.choice(interior, sample_size, replace=False)

    # Maximum distance to consider (to avoid boundary effects)
    max_dist = min(R, L//2) * 2  # rough estimate

    # Accumulate counts per distance
    count_sum = np.zeros(max_dist+1)
    for source in sample:
        dists = bfs_distances(adj, source, max_dist)
        # Count nodes at each exact distance
        for d in range(max_dist+1):
            cnt = sum(1 for dd in dists.values() if dd == d)
            count_sum[d] += cnt
    # Average
    avg_count = count_sum / sample_size

    # Compute cumulative balls
    ball_vol = np.cumsum(avg_count)

    # Fit power law for large r (excluding small r to avoid lattice artifacts)
    r_vals = np.arange(10, max_dist, dtype=float)
    y_vals = ball_vol[r_vals]
    # Fit log(r) vs log(y)
    coeffs = np.polyfit(np.log(r_vals), np.log(y_vals), 1)
    d_fit = coeffs[0]
    print(f"Fitted growth exponent d = {d_fit:.3f}")

    # Plot
    plt.figure()
    plt.loglog(range(len(ball_vol)), ball_vol, 'o', label='Data')
    plt.loglog(r_vals, np.exp(coeffs[1]) * r_vals**d_fit, '--', label=f'Fit d={d_fit:.2f}')
    plt.xlabel('Distance r')
    plt.ylabel('Ball volume |B_r|')
    plt.title('HCP lattice growth')
    plt.legend()
    plt.savefig('growth_fit.pdf')
    plt.savefig('growth_fit.png')
    print("Saved growth_fit.pdf")

if __name__ == "__main__":
    main()
