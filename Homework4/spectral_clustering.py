import numpy as np
from scipy.sparse import csr_matrix, diags
from scipy.sparse.linalg import eigsh   # sparse symmetric eigen solver
from sklearn.cluster import KMeans
from pathlib import Path

# Loading graph data
def load_graph(path: Path):
    """
    Real graph: 2-columns CSV-like .dat
    Each line: i,j (integers) meaning an undirected edge between i and j
    """
    edges = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) < 2:
                continue
            u = int(parts[0])
            v = int(parts[1])
            if u == v:
                continue
            edges.append((u, v))

    # Map node IDs to 0..n-1
    nodes = sorted(set([u for u, v in edges] + [v for u, v in edges]))
    id_to_idx = {node_id: i for i, node_id in enumerate(nodes)}
    n = len(nodes)

    # Build unweighted symmetric adjacency (similarity) matrix W
    row_idx = []
    col_idx = []
    data = []
    for (u, v) in edges:
        i = id_to_idx[u]
        j = id_to_idx[v]
        row_idx.extend([i, j])
        col_idx.extend([j, i])
        data.extend([1.0, 1.0])

    W = csr_matrix((data, (row_idx, col_idx)), shape=(n, n))
    return W, nodes


def load_synthetic_graph(path: Path):
    """
    Synthetic graph: 3-columns .dat
    Each line: i,j,weight (all integers).
    """
    edges = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) < 3:
                continue
            u = int(parts[0])
            v = int(parts[1])
            w = int(parts[1])
            if u == v:
                continue
            edges.append((u, v, w))

    nodes = sorted(set([u for u, v, w in edges] + [v for u, v, w in edges]))
    id_to_idx = {node_id: i for i, node_id in enumerate(nodes)}
    n = len(nodes)

    row_idx = []
    col_idx = []
    data = []
    for (u, v, w) in edges:
        i = id_to_idx[u]
        j = id_to_idx[v]
        row_idx.extend([i, j])
        col_idx.extend([j, i])
        data.extend([w, w])

    W = csr_matrix((data, (row_idx, col_idx)), shape=(n, n))
    return W, nodes


# Spectral clustering core (Ng-Jordan-Weiss)
def spectral_clustering(W, k, return_eigenvalues=False):
    """
    Perform normalized spectral clustering on a similarity (adjacency) matrix " (sparse CSR).

    Parameters
    ----------
    W : csr_matrix, shape (n, n)
        Symmetric similarity matrix (non-negative).
    k : int
        Number of clusters.
    return_eigenvalues : bool
        If True, also return the eigenvalues used.

    Returns
    -------
    labels : ndarray, shape (n,)
        Cluster label for each node (0...k-1).
    evals (optional) : ndarray, shape (k,)
        The k smallest eigenvalues of the normalized Laplacian.
    """
    n = W.shape[0]

    # 1. Degree matrix D (we store only the diagonal as a vector)
    degrees = np.array(W.sum(axis=1)).flatten()     # shape (n,)
    # Prevent division by zero for isolated nodes
    degrees[degrees == 0] = 1.0

    # 2. Normalized Laplacian L = I - D^{-1/2} W D^{-1/2}
    # Build D^{-1/2} (inverse square root of degrees)
    d_inv_sqrt = 1.0 / np.sqrt(degrees)
    D_inv_sqrt = diags(d_inv_sqrt)      # Turning it into a diagonal matrix

    # Compute normalized Laplacian
    # L = I - D^{-1/2} W D^{-1/2}
    I = diags(np.ones(n))
    L = I - D_inv_sqrt @ W @ D_inv_sqrt

    # 3. Compute k smallest eigenvectors of L
    # eigsh returns eigenvalues in ascending order by default if which="SM"
    evals, evecs = eigsh(L, k=k, which="SM")

    # 4. Form matrix U from eigenvectors (columns)
    U = evecs   # shape (n, k)

    # 5. Row-normalize U (so each row has length 1)
    row_norms = np.linalg.norm(U, axis=1, keepdims=True)
    # avoid division by zero
    row_norms[row_norms == 0] = 1.0
    T = U / row_norms

    # 6. Run k-means on rows of T
    kmeans = KMeans(n_clusters=k, n_init=10)
    labels = kmeans.fit_predict(T)

    if return_eigenvalues:
        return labels, evals
    else:
        return labels


def estimate_k_from_eigengap(W, max_k=10):
    """
    Simple helper to *suggest* a number of clusters using the eigengap heuristic.

    1. Compute the first max_k+1 eigenvalues of L.
    2. Look for the largest gap between constructive eigenvalues.
    3. Return k at that gap.

    This does NOT replace domain knowledge, but it helps exploration.
    """
    n = W.shape[0]
    degrees = np.array(W.sum(axis=1)).flatten()
    degrees[degrees == 0] = 1.0
    d_inv_sqrt = 1.0 / np.sqrt(degrees)
    D_inv_sqrt = diags(d_inv_sqrt)
    I = diags(np.ones(n))
    L = I - D_inv_sqrt @ W @ D_inv_sqrt

    # Compute first max_k+1 smallest eigenvalues
    m = max_k + 1
    evals, _ = eigsh(L, k=m, which="SM")
    evals = np.sort(evals)

    # Compute gaps
    gaps = evals[1:] - evals[:-1]
    k_hat = np.argmax(gaps[:max_k]) + 1     # -1 because gap[i] is between i and i+1

    return k_hat, evals
