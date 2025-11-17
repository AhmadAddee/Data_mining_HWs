import argparse
import math
import time
from apriori_core import count_singletons_and_total, apriori
from rules import generate_rules


# Prints frequent itemsets per k and totals
def print_frequent_itemsets(frequent):
    total_sets = 0
    for k in sorted(frequent.keys()):
        print(f"\n=== Frequent {k}-itemsets (count = {len(frequent[k])}) ===")
        for tup, cnt in sorted(frequent[k].items(), key=lambda x: (-x[1], x[0])):
            print(f"{tup}  : {cnt}")
            total_sets += 1
    print(f"\nTotal frequent itemsets found: {total_sets}")


# Prints all rules sorted by confidence then support
def print_rules(rules):
    print(f"\n=== Association rules (sorted by confidence desc, then support desc) ===")
    if not rules:
        print("No rules found with the specified confidence threshold.")
        return
    for i, r in enumerate(rules, 1):
        lhs = ",".join(r['lhs'])
        rhs = ",".join(r['rhs'])
        print(f"{i:4d}. {lhs} -> {rhs}    (support={r['support']}, confidence={r['confidence']:.4f})")

 
def parse_args():
    p = argparse.ArgumentParser(description="Apriori CLI (percent support -> absolute). Prints all rules.")
    p.add_argument("--path", type=str, required=True, help="Path to transaction file")
    p.add_argument("--min_support", type=int, default=None, help="Absolute min support (overrides percent)")
    p.add_argument("--min_support_percent", type=float, default=1.0, help="Percent support (default 1.0)")
    p.add_argument("--min_conf", type=float, default=0.5, help="Minimum confidence (default 0.5)")
    return p.parse_args()


def main():
    args = parse_args()
    path = args.path

    overall_start = time.perf_counter()
    t0 = time.perf_counter()
    singleton_counts, total_trx = count_singletons_and_total(path)
    t1 = time.perf_counter()
    time_singleton_pass = t1 - t0

    print(f"Dataset: {path}")
    print(f"Total transactions (counted): {total_trx}")

    if args.min_support is not None:
        min_support = args.min_support
        print(f"Using absolute min_support = {min_support}")
    else:
        pct = args.min_support_percent
        if pct <= 0 or pct > 100:
            raise ValueError("min_support_percent must be in (0,100].")
        min_support = max(1, math.floor(total_trx * (pct/100.0))) # Convert percentage to absolute support
        print(f"Using min_support_percent = {pct}% -> absolute min_support = {min_support}")

    t2 = time.perf_counter()
    frequent, timing = apriori(path, min_support)
    t3 = time.perf_counter()
    apriori_time = t3 - t2

    print_frequent_itemsets(frequent)

    print("\n=== Timing summary ===")
    print(f"Singleton counting pass time: {time_singleton_pass:.4f} sec")
    print(f"Apriori total time: {apriori_time:.4f} sec")
    print(f"(End-to-end elapsed = {time.perf_counter() - overall_start:.4f} sec)")
    print("\n=== Per-level timings ===")
    # C1
    print(f"C1: {timing['C_times'].get(1, 0.0):.4f} sec   L1: {timing['L_times'].get(1, 0.0):.4f} sec")
    for k in sorted({*timing['C_times'].keys(), *timing['L_times'].keys()}):
        if k == 1:
            continue
        c = timing['C_times'].get(k)
        l = timing['L_times'].get(k)
        if c is not None or l is not None:
            print(f"C{k}: {0.0 if c is None else c:.4f} sec   L{k}: {0.0 if l is None else l:.4f} sec")

    rules_start = time.perf_counter()
    rules = generate_rules(frequent, args.min_conf)
    rules_end = time.perf_counter()
    print(f"\nRules generation time: {rules_end - rules_start:.4f} sec")

    print_rules(rules)


if __name__ == "__main__":
    main()
