import gzip
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
from triest_base import TriestBase as Triest
#from triest_impr import TriestImpr as Triest

TRUE_TRIANGLES = 8910005


def read_stream_data(path: Path):
    """
    Stream edges from a gzipped SNAP file.

    Each non-comment line is 'u v'. Nodes are converted to int.
    The file is read line-by-line so memory stays small.
    """
    with gzip.open(path, "rt") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            u, v = parts[0], parts[1]
            if u == v:
                continue
            yield int(u), int(v)


def run_experiment(file_path: Path, Ms):
    errors = []
    estimates = []

    for M in Ms:
        print(f"Running TRIÈST with M={M}....")
        tb = Triest(M=M)
        for u, v in read_stream_data(file_path):
            tb.process_edges(u, v)

        est = tb.estimate_global()
        estimates.append(est)

        relative_error = abs(est - TRUE_TRIANGLES) / TRUE_TRIANGLES
        errors.append(relative_error)

        print(f"    estimate: {est:.2f}, rel.error={relative_error:.4f}")
        print(f"    sample size: {tb.sample_size}, edges seen: {tb.t}\n")

    return estimates, errors


def plot_results(Ms, estimates, errors):
    plt.figure(figsize=(12, 5))

    # Plot estimates
    plt.subplot(1,2,1)
    plt.plot(Ms, estimates, marker='o')
    plt.axhline(TRUE_TRIANGLES, color='red', linestyle='--', label='True')
    plt.xlabel('Reservoir size M')
    plt.ylabel('Triangle estimate')
    plt.title('Estimated triangles vs M')
    plt.legend()

    # Plot relative errors
    plt.subplot(1,2,2)
    plt.plot(Ms, errors, marker='o')
    plt.xlabel('Reservoir size M')
    plt.ylabel('Relative error')
    plt.title('Relative error vs M')

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reservoir Sampling")
    parser.add_argument("--data-file", "-d", type=str, required=True, help="The path of the dataset.")
    parser.add_argument("--memory", "-m", type=int, default=100000, nargs="+", help="Reservoir size M (max edges to keep).")
    parser.add_argument("--plot", action="store_true", help="Disable plotting (just print results).")
    args = parser.parse_args()

    Ms = args.memory

    if len(Ms) == 1:
        M = Ms[0]
        tb = Triest(M=M)
        for (u, v) in read_stream_data(Path(args.data_file)):
            tb.process_edges(u, v)
        est_global = tb.estimate_global()
        print(f"Estimated number of triangels: {est_global:.2f}")
        print(f"Sample size used: {tb.sample_size}")
        print(f"Edges seen (t): {tb.t}")
        print(f"Relative error vs SNAP: {abs(est_global - TRUE_TRIANGLES) / TRUE_TRIANGLES:.4f}")
    else:
        # "./dataset/web-NotreDame.txt.gz"
        estimates, errors = run_experiment(Path(args.data_file), Ms=Ms)
        if args.plot:
            plot_results(Ms, estimates, errors)
