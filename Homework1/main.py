import os
import argparse
import itertools
from pathlib import Path
from find_similar_items import Shingling , CompareSets, MinHashing, CompareSignatures, LSH
from doc_processor import read_zipped_docs, get_text_dict

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
    # parser.add_argument("--seed", "-s", type=int, default=42, help="Random seed for MinHash hash families")

    args = parser.parse_args()

    if args.zipfile:
        file_path = Path(os.path.dirname(Path(args.zipfile)))
        file_name = os.path.basename(Path(args.zipfile))
        docs = get_text_dict(read_zipped_docs(file_path, file_name, args.num_of_docs))
    else:
        docs = get_text_dict([Path(doc) for doc in args.docs] if args.docs else None)

    bands = args.bands
    if bands is None:
        bands = LSH.choose_bands(args.signature_length, args.threshold)

    print(f"Finding similar documents in the corpus: {len(docs)} documents, "
          f"where length of shingle is {args.shingle_length}, length of MinHash signature is {args.signature_length}, "
          f"similarity threshold is {args.threshold}, number of bands is {bands}")

    hashed, exact, sigs, est, candidates = perform_lsh(docs, args.shingle_length, args.signature_length, args.threshold, bands)

    print_result(hashed, exact, sigs, est, candidates, bands, args.shingle_length, args.shingle_length, args.threshold)


"""
py .\Data_mining_HWs\Homework1\main.py --d "C:\\Skolan\\TSEDM1\\Data mining ID2222\\Data_mining_HWs\\Homework1\\dataset\\mini_newsgroups\\alt.atheism\\51121" "C:\\Skolan\\TSEDM1\\Data mining ID2222\\Data_mining_HWs\\Homework1\\dataset\\mini_newsgroups\\alt.atheism\\51126" -k 2 -n 128 -t 0.8 -b 8
py .\Data_mining_HWs\Homework1\main.py -z "C:\\Skolan\\TSEDM1\\Data mining ID2222\\Data_mining_HWs\\Homework1\\dataset\\twenty+newsgroups.zip" -nod 1000 -k 2 -n 128 -t 0.8 -b 8
py .\Data_mining_HWs\Homework1\main.py -nod 100 -k 3 -n 10 -t 0.8 -b 5
"""