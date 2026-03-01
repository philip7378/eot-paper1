#!/usr/bin/env python3
"""
fig3_prism_motif.py

Draw the six‑node triangular prism motif and an external node with three connections.
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'paper0'))
from geom_hcp import make_hcp_positions, build_adj_from_positions

def main():
    # Build positions for a small patch
    pos_dict = make_hcp_positions(R=4, L=5, a=1.0)
    # Identify the prism motif: nodes in layer 2 and 3 with certain coordinates
    # For a clean figure, we'll use a subset and manually define connections.
    # Alternatively, we can compute positions for specific indices.
    # Let's pick nodes with (i,j,k) as in the paper:
    motif_coords = []
    motif_nodes = [(0,0,2), (1,0,2), (0,1,2), (0,0,3), (1,0,3), (0,1,3)]
    for n in motif_nodes:
        if n in pos_dict:
            motif_coords.append(pos_dict[n])
    motif_coords = np.array(motif_coords)

    # External node above (should have three connections)
    external = (0.5, 0.5, 3.5)  # approximate, adjust as needed

    # Plot
    fig = plt.figure(figsize=(10,8))
    ax = fig.add_subplot(111, projection='3d')

    # Plot motif nodes
    ax.scatter(motif_coords[:,0], motif_coords[:,1], motif_coords[:,2],
               c='blue', s=100, label='Motif nodes')

    # Plot external node
    ax.scatter(*external, c='green', s=200, marker='^', label='External node')

    # Draw edges between motif nodes (prism)
    # Bottom triangle (first three)
    for i in range(3):
        for j in range(i+1,3):
            ax.plot([motif_coords[i,0], motif_coords[j,0]],
                    [motif_coords[i,1], motif_coords[j,1]],
                    [motif_coords[i,2], motif_coords[j,2]], 'gray', linestyle='--')
    # Top triangle (last three)
    for i in range(3,6):
        for j in range(i+1,6):
            ax.plot([motif_coords[i,0], motif_coords[j,0]],
                    [motif_coords[i,1], motif_coords[j,1]],
                    [motif_coords[i,2], motif_coords[j,2]], 'gray', linestyle='--')
    # Vertical edges
    for i in range(3):
        ax.plot([motif_coords[i,0], motif_coords[i+3,0]],
                [motif_coords[i,1], motif_coords[i+3,1]],
                [motif_coords[i,2], motif_coords[i+3,2]], 'gray', linestyle='--')

    # Draw edges from external node to top triangle
    for i in range(3,6):
        ax.plot([external[0], motif_coords[i,0]],
                [external[1], motif_coords[i,1]],
                [external[2], motif_coords[i,2]], 'green', linewidth=3)

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.set_title('Figure 3: Triangular prism motif and odd boundary node')
    ax.legend()
    plt.tight_layout()
    plt.savefig('fig3_prism_motif.pdf')
    plt.savefig('fig3_prism_motif.png')
    print("Saved fig3_prism_motif.pdf")

if __name__ == "__main__":
    main()
