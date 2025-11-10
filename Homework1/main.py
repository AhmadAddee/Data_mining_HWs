import os
import argparse
import itertools
from pathlib import Path
from find_similar_items import Shingling , CompareSets, MinHashing, CompareSignatures, LSH
from doc_processor import read_zipped_docs, get_text_dict
import benchmark

def perform_lsh(docs: dict[str, str], k: int, signature_len: int, threshold: float, bands: int):
    # Shingles
    sh = Shingling(k=k)
    hashed: dict[str, list[int]] = {doc_id: sh.shingles(txt) for doc_id, txt in docs.items()}

    # Exact Jaccard
    exact: dict[tuple[str, str], float] = {}
    for a, b in itertools.combinations(sorted(docs.keys()), 2):
        exact[(a, b)] = CompareSets.jaccard(hashed[a], hashed[b])

    # MinHash signatures
    mh = MinHashing(signature_len=signature_len)
    sigs: dict[str, list[int]] = {doc_id: mh.get_signature(hashed_set) for doc_id, hashed_set in hashed.items()}

    # LSH
    lsh = LSH(bands=bands)
    candidates = lsh.candidate_pairs(sigs, t=threshold)

    est: dict[tuple[str, str], float] = {}
    for a, b in itertools.combinations(sorted(docs.keys()), 2):
        est[(a, b)] = CompareSignatures.estimate(sigs[a], sigs[b])

    return hashed, exact, sigs, est, candidates

def print_result(hashed: dict[str, list[int]], exact: dict[tuple[str, str], float], sigs: dict[str, list[int]],
        est: dict[tuple[str, str], float],
        candidates: set[tuple[str, str]],
        bands: int,
        k: int,
        siglen: int,
        lsh_threshold: float,
):
    print("Parameters:")
    print(f"  k (shingle length): {k}")
    print(f"  signature length:  {siglen}")
    print(f"  LSH bands:         {bands} (rows per band = {siglen // bands})")
    print(f"  LSH threshold t:   {lsh_threshold}")
    print()

    print("Doc -> #unique hashed shingles:")
    for doc_id in sorted(hashed):
        print(f"  {doc_id}: {len(hashed[doc_id])}")
    print()

    print("Pairwise similarities (exact Jaccard vs. MinHash estimate):")
    for (a, b) in sorted(exact):
        print(f"  {a} vs {b}: exact={exact[(a,b)]:.3f}  est={est[(a,b)]:.3f}")
    print()

    if candidates:
        print("LSH candidate pairs (signature agreement ≥ t):")
        for a, b in sorted(candidates):
            print(f"  {a} ~ {b}")
    else:
        print("LSH candidate pairs: (none)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find similar documents in a corpus using Shingling, Min-Hashing, and LSH.")
    parser.add_argument("--zipfile", "-z", type=str, default=None, help="The name of the zipfile to fetch the dataset from.")
    parser.add_argument("--num-of-docs", "-nod", type=int, default=10, help="The number of files to read in from the zip file")
    parser.add_argument("--docs", "-d", nargs='+', default=None, help="List of document file paths to compare.")
    parser.add_argument("--shingle-length", "-k", type=int, default=10, help="Length of each shingle.")
    parser.add_argument("--signature-length", "-n", type=int, default=100, help="Length of MinHash signature.")
    parser.add_argument("--threshold", "-t", type=float, default=0.8, help="Similarity threshold for LSH.")
    parser.add_argument("--bands", "-b", type=int, default=None, help="Number of bands for LSH")

    # Only for benchmarking grid
    parser.add_argument("--benchmark", action="store_true", help="Run timing grid an write CSV (see grid flags below).")
    parser.add_argument("--grid-k", type=str, default="10", help="Comma-separated k values, e.g. '8,10,12'")
    parser.add_argument("--grid-siglen", type=str, default="128", help="Comma-separated signature lenghts, e.g. '64, 128, 256'")
    parser.add_argument("--grid-threshold", type=str, default="0.8", help="Comma-separated thresholds, e.g. '0.7, 0.8, 0.9'")
    parser.add_argument("--grid-bands", type=str, default="auto", help="Comma-separated bands or 'auto', e.g. 'auto' or '8,16'.")
    parser.add_argument("--sizes", type=str, default="", help="Comma-separated corpus sizes, e.g. '5,10,20'. Defaults: use all sizes up to N.")
    parser.add_argument("--repeats", type=int, default=1, help="Number of repeats per grid point (averaged for plots).")
    parser.add_argument("--csv-out", type=str, default="benchmark.csv", help="Output CSV path.")
    parser.add_argument("--plot-out", type=str, default="", help="Optional PNG path for runtime vs. size plot.")

    args = parser.parse_args()

    if args.zipfile:
        file_path = Path(os.path.dirname(Path(args.zipfile)))
        file_name = os.path.basename(Path(args.zipfile))
        docs = get_text_dict(read_zipped_docs(file_path, file_name, args.num_of_docs))
    else:
        docs = get_text_dict([Path(doc) for doc in args.docs] if args.docs else None)

    # Only for benchmarking grid
    # ------------------------------
    if args.benchmark:
        if args.sizes.strip():
            sizes = benchmark._parse_int_list(args.sizes)
        else:
            N = len(docs)
            sizes = sorted({min(5, N), max(N // 2, 2), N})

        k_list = benchmark._parse_int_list(args.grid_k)
        siglens = benchmark._parse_int_list(args.grid_siglen)
        trhesholds = benchmark._parse_float_list(args.grid_threshold)
        bands_list = [s.strip() for s in args.grid_bands.split(",") if s.strip()]

        plot_out = args.plot_out if args.plot_out.strip() else None

        benchmark.run_benchmark_grid(
            docs=docs,
            sizes=sizes,
            k_list=k_list,
            siglens=siglens,
            thresholds=trhesholds,
            bands_list=bands_list,
            repeats=max(1, args.repeats),
            csv_out=args.csv_out,
            plot_out=plot_out,
        )
        print(f"[OK] Wrote CSV to {args.csv_out}" + (f" and plot to {plot_out}" if plot_out else ""))
        exit(0)
    #---------------------------------
    
    bands = args.bands
    if bands is None:
        bands = LSH.choose_bands(args.signature_length, args.threshold)

    print(f"Finding similar documents in the corpus: {len(docs)} documents, "
          f"where length of shingle is {args.shingle_length}, length of MinHash signature is {args.signature_length}, "
          f"similarity threshold is {args.threshold}, number of bands is {bands}")

    hashed, exact, sigs, est, candidates = perform_lsh(docs, args.shingle_length, args.signature_length, args.threshold, bands)

    print_result(hashed, exact, sigs, est, candidates, bands, args.shingle_length, args.shingle_length, args.threshold)
