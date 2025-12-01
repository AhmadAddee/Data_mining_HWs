import os

from spectral_clustering import load_graph, load_synthetic_graph
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
    axes[0].bar(range(1, n+1), eigenvalues[:n], color='steelblue')
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
        try:
            A_sorted = np.asarray(A_sorted, dtype=float)
        except ValueError:
            # fallback: convert row-by-row (handles nested sequences)
            A_sorted = np.array([np.array(row, dtype=float) for row in A_sorted])

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
    parser = argparse.ArgumentParser(description="Spectral csustering")
    parser.add_argument("--data-file", "-d", type=str, required=True, help="The path of the dataset.")
    parser.add_argument("--communities", "-k", type=int, nargs="+", help="Value of k.")
    parser.add_argument("--plot", action="store_true", help="Disable plotting (just print results).")
    args = parser.parse_args()

    k = args.communities
    datafile = args.data_file

    W_real, nodes_real = load_graph(Path(datafile))
    k_real, evals_real = estimate_k_from_eigengap(W_real, max_k=10)
    if not k:
        k_real, evals_real = estimate_k_from_eigengap(W_real, max_k=10)
    print("Suggested k for real graph:", k_real, "eigenvalues:", evals_real)
    labels_real = spectral_clustering(W_real, k=k_real)

    if args.plot:
        path = os.getcwd()
        plot_results(W_real, evals_real, labels_real, "Real plt", f"{path}/result.png")
