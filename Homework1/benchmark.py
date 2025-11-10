import csv
import time
import itertools

from find_similar_items import Shingling , CompareSets, MinHashing, CompareSignatures, LSH


def _subset_docs(docs: dict[str, str], n: int) -> dict[str, str]:
    keys = sorted(docs.keys())[:max(0, min(n, len(docs)))]
    return {k: docs[k] for k in keys}

def _time_build_pipeline(docs: dict[str, str], k: int, siglen: int, lsh_threshold: float, bands: int) -> tuple[dict[str, list[int]], dict[tuple[str, str], float], dict[str, list[int]], dict[tuple[str, str], float], set[tuple[str, str]], dict[str, float]]:
    t0 = time.perf_counter()
    sh = Shingling(k=k)
    hashed: dict[str, list[int]] = {doc_id: sh.shingles(txt) for doc_id, txt in docs.items()}
    t1 = time.perf_counter()

    exact: dict[tuple[str, str], float] = {}
    for a, b in itertools.combinations(sorted(docs.keys()), 2):
        exact[(a, b)] = CompareSets.jaccard(hashed[a], hashed[b])
    t2 = time.perf_counter()

    mh = MinHashing(signature_len=siglen)
    sigs: dict[str, list[int]] = {doc_id: mh.get_signature(hashed_set) for doc_id, hashed_set in hashed.items()}
    t3 = time.perf_counter()

    lsh = LSH(bands=bands)
    candidates = lsh.candidate_pairs(sigs, t=lsh_threshold)
    t4 = time.perf_counter()

    est: dict[tuple[str, str], float] = {}
    for a, b in itertools.combinations(sorted(docs.keys()), 2):
        est[(a, b)] = CompareSignatures.estimate(sigs[a], sigs[b])

    timing_ms = {
        "t_shingle_ms": (t1 - t0) * 1000.0,
        "t_exact_ms": (t2 - t1) * 1000.0,
        "t_minhash_ms": (t3 - t2) * 1000.0,
        "t_lsh_ms": (t4 - t3) * 1000.0,
        "t_total_ms": (t4 - t0) * 1000.0,
    }
    return hashed, exact, sigs, est, candidates, timing_ms

def _mean_abs_error(exact: dict[tuple[str, str], float], est: dict[tuple[str, str], float]) -> float:
    if not exact:
        return 0.0
    errs = [abs(exact[p] - est[p]) for p in exact.keys()]
    return sum(errs) / len(errs)

def _parse_int_list(s: str) -> list[int]:
    return [int(x.strip()) for x in s.split(",") if x.strip()]

def _parse_float_list(s: str) -> list[float]:
    return [float(x.strip()) for x in s.split(",") if x.strip()]

def run_benchmark_grid(
        docs: dict[str, str],
        sizes: list[int],
        k_list: list[int],
        siglens: list[int],
        thresholds: list[float],
        bands_list: list[str],
        repeats: int,
        csv_out: str,
        plot_out: str | None = None,
):
    sizes = sorted({min(s, len(docs)) for s in sizes if s > 1})
    if not sizes:
        raise ValueError("No valid sizes (need at least 2 and =< number of docs).")

    rows_for_plot = []
    with open(csv_out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow([
            "n_docs", "k", "signature_len", "threshold", "bands", "rows_per_band",
            "candidate_pairs", "pairs_total", "mean_abs_error",
            "t_shingle_ms", "t_exact_ms", "t_minhash_ms", "t_lsh_ms", "t_total_ms"
        ])

        for n_docs in sizes:
            sub_docs = _subset_docs(docs, n_docs)

            for k in k_list:
                for siglen in siglens:
                    for thr in thresholds:
                        for b_item in bands_list:
                            if b_item.strip().lower() == "auto":
                                b = LSH.choose_bands(siglen, thr)
                            else:
                                b = int(b_item)
                                if siglen % b != 0:
                                    continue

                            round_rows = []
                            for _ in range(max(1, repeats)):
                                hashed, exact, sigs, est, candidates, tms = _time_build_pipeline(
                                    sub_docs, k=k, siglen=siglen, lsh_threshold=thr, bands=b
                                )
                                mae = _mean_abs_error(exact, est)
                                pairs_total = len(exact)

                                w.writerow([
                                    n_docs, k, siglen, thr, b, (siglen // b),
                                    len(candidates), pairs_total, f"{mae:.6f}",
                                    f"{tms['t_shingle_ms']:.3f}", f"{tms['t_exact_ms']:.3f}",
                                    f"{tms['t_minhash_ms']:.3f}", f"{tms['t_lsh_ms']:.3f}",
                                    f"{tms['t_total_ms']:.3f}",
                                ])
                                round_rows.append((n_docs, tms["t_total_ms"]))

                            if repeats > 1 and round_rows:
                                avg_total = sum(t for _, t in round_rows) / len(round_rows)
                                rows_for_plot.append((n_docs, k, siglen, thr, b, avg_total))
                            elif round_rows:
                                rows_for_plot.append((n_docs, k, siglen, thr, b, round_rows[0][1]))

    if plot_out:
        try:
            import matplotlib.pyplot as plt
            params = {(k, s, t, b) for _, k, s, t, b, _ in rows_for_plot}
            if len(params) == 1:
                series = sorted(rows_for_plot, key=lambda r: r[0])
                xs = [r[0] for r in series]
                ys = [r[5] for r in series]
                (k, siglen, thr, b) = list(params)[0]

                plt.figure()
                plt.plot(xs, ys, marker="o")
                plt.title(f"Runtime vs. corpus size (k={k}, siglen={siglen}, t={thr}, bands={b})")
                plt.xlabel("Number of documents")
                plt.ylabel("Total runtime (ms)")
                plt.grid(True, linestyle="--", alpha=0.5)
                plt.tight_layout()
                plt.savefig(plot_out, dpi=150)
                plt.close()
        except Exception as exp:
            print(f"Didn't plot, {exp}")
            pass
