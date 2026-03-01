#!/usr/bin/env python3
"""
fig2_hcp_lattice.py

Draw a 3D scatter plot of a small HCP patch with layers colored by parity.
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'paper0'))
from geom_hcp import make_hcp_positions, build_adj_from_positions

def main():
    # Generate a small patch
    pos_dict = make_hcp_positions(R=3, L=4, a=1.0)
    # Extract coordinates and layer parity
    nodes = list(pos_dict.keys())
    coords = np.array([pos_dict[v] for v in nodes])
    layers = np.array([v[2] for v in nodes])
    parity = layers % 2
    colors = ['red' if p==0 else 'blue' for p in parity]

    fig = plt.figure(figsize=(10,8))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(coords[:,0], coords[:,1], coords[:,2], c=colors, s=50, alpha=0.8)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.set_title('Figure 2: HCP lattice with alternating layers (red: even, blue: odd)')
    plt.tight_layout()
    plt.savefig('fig2_hcp_lattice.pdf')
    plt.savefig('fig2_hcp_lattice.png')
    print("Saved fig2_hcp_lattice.pdf")

if __name__ == "__main__":
    main()
