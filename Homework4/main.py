import os

from spectral_clustering import load_graph
from spectral_clustering import spectral_clustering, estimate_k_from_eigengap
from pathlib import Path
from matplotlib import pyplot as plt
import numpy as np
import argparse


def plot_results(A, eigenvalues, labels, name, filename):
    """Generate visualization plots."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Plot 1: Eigenvalue spectrum (helps visualize eigengap for choosing k)
    n = min(20, len(eigenvalues))
    axes[0].plot(range(1, n+1), eigenvalues[:n], marker='o')
    axes[0].set_ylim(0, max(eigenvalues[:n]) * 1.1)
    axes[0].set_xlabel('Eigenvalue Index')
    axes[0].set_ylabel('Eigenvalue')
    axes[0].set_title(f'{name} - Eigenvalues')
    axes[0].grid(True, alpha=0.3)

    # Plot 2: Adjacency matrix reordered by cluster (shows block structure)
    order = np.argsort(labels)
    A_sorted = A[order][:, order]
    # Ensure numeric float dtype for plotting (convert object or other types to float)
    # Handle scipy sparse matrices and object-dtype arrays (e.g., list-of-lists)
    if hasattr(A_sorted, "toarray"):
        # scipy sparse matrix -> convert to dense numpy array
        A_sorted = A_sorted.toarray().astype(float)
    else:
        A_sorted = np.asarray(A_sorted, dtype=float)

    im = axes[1].imshow(A_sorted, cmap='Blues')
    axes[1].set_title(f'{name} - Adjacency Matrix (by cluster)')
    axes[1].set_xlabel('Node Index')
    axes[1].set_ylabel('Node Index')
    # show color scale for the adjacency values
    fig.colorbar(im, ax=axes[1], fraction=0.046, pad=0.04)

    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"Saved: {filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spectral clustering on different graphs")
    parser.add_argument("--data-dir", "-d", type=str, required=True, help="Folder containing the graph .dat files.")
    parser.add_argument("--communities", "-k", type=int, help="Number of communities k (if omitted, use eigengap heuristic).")
    parser.add_argument("--plot", action="store_true", help="Enable plotting and save result images.")
    args = parser.parse_args()

    k = args.communities
    data_dir = args.data_dir
    real_data_path = f"{data_dir}/example1.dat"
    syn_data_path  = f"{data_dir}/example2.dat"

    A_real, nodes_real = load_graph(real_data_path)
    if k is None:
        k_real, evals_real = estimate_k_from_eigengap(A_real, max_k=10)
    else:
        k_real = k
        _, evals_real = estimate_k_from_eigengap(A_real, max_k=10)

    print("Suggested k for real graph:", k_real, "eigenvalues:", evals_real)
    labels_real = spectral_clustering(A_real, k=k_real)

    if args.plot:
        plot_results(A_real, evals_real, labels_real, "Eigenvalues", f"{data_dir}/example1.png")

    A_syn, nodes_syn = load_graph(syn_data_path)
    if k is None:
        k_syn, evals_syn = estimate_k_from_eigengap(A_syn, max_k=10)
    else:
        k_syn = k
        _, evals_syn = estimate_k_from_eigengap(A_syn, max_k=10)

    print("Suggested k for synthetic graph:", k_syn, "eigenvalues:", evals_syn)
    labels_syn = spectral_clustering(A_syn, k=k_syn)

    if args.plot:
        plot_results(A_syn, evals_syn, labels_syn, "Eigenvalues", f"{data_dir}/example2.png")
