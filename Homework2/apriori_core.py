import itertools
import time

# Yields one transaction per line as a list of item strings
def transactions_generator(path):
    """Yield parsed transactions (lists of item strings) from file at path.""" 
    with open(path, 'r') as f: 
        for ln in f: 
            parts = ln.split()
            if parts: # Incase blank line
                yield parts 


# Counts single items (1-itemset supports) and total number of transactions
def count_singletons_and_total(path):
    """
    First fast pass: count single items and return total transaction count.
    Returns (counts_map item->count, total_transactions)
    """
    counts = {}
    total_trx = 0
    for trx in transactions_generator(path): 
        total_trx += 1
        for item in set(trx):
            counts[item] = counts.get(item, 0) + 1
    return counts, total_trx


# Generates candidate k-itemsets from frequent (k-1)-itemsets (join + prune)
def candidate_gen(prev_L, k): # prev_L: list of frozensets. k: size of the candidate itemset.
    """Generate candidate k-itemsets from L_{k-1} using join + prune."""
    candidates = set()
    prev_list = []
    for x in prev_L:
        prev_list.append(tuple(sorted(x))) # Sort each itemset to ensure consistent ordering
    prev_set = set(prev_L) # Set for quick membership tests
    n = len(prev_list) 
    for i in range(n): #
        for j in range(i + 1, n): 
            a = prev_list[i]
            b = prev_list[j]
            if a[:k - 2] == b[:k - 2]: 
                # union the two (k-1)-itemsets
                cand_set = set(a) | set(b)
                if len(cand_set) == k:
                    # prune: all (k-1)-subsets must be in prev_L
                    cand_items = tuple(cand_set)
                    for subset in itertools.combinations(cand_items, k - 1): # If k = 4, combine 3 of 4 items in different ways and check if they exist in prev_set
                        if frozenset(subset) not in prev_set:
                            break
                    else: # If all (k-1)-subsets are in prev_set, add the candidate to the set of candidates
                        candidates.add(frozenset(cand_set)) 
    return candidates


def count_candidates(path, candidates):
    """Count support for candidate itemsets by a single pass through transactions."""
    counts = {}
    for c in candidates:
        counts[c] = 0
    if not candidates:
        return {} 
    k = len(next(iter(candidates))) # Get the size of the first candidate itemset
    for trx in transactions_generator(path):
        trxset = set(trx)
        if len(trxset) < k: # If the transaction has less items than the size of the candidate itemset, skip it
            continue
        for cand in candidates: # Check if the candidate is a subset of the transaction
            if cand.issubset(trxset):
                counts[cand] += 1
    return counts


# Runs Apriori with an absolute min_support, returns frequent itemsets and timings
def apriori(path, min_support):
    """
    Run Apriori using an absolute min_support (count). Returns:
     - frequent_itemsets: dict k -> { tuple(sorted items) : support_count }
     - timing_info: dict with per-level times:
         * 'total_transactions'
         * 'C_times': {k: seconds to construct Ck} (C1 is 0.0)
         * 'L_times': {k: seconds to compute Lk}
    """
    timing = {'C_times': {}, 'L_times': {}} 

    # L1 timing (singleton pass + filtering)
    t_L1_start = time.perf_counter()
    single_counts, total_trx = count_singletons_and_total(path)
    timing['total_transactions'] = total_trx
    # C1 is all items (no candidate generation needed)
    timing['C_times'][1] = 0.0

    # Filter singletons by min_support
    L1 = {}
    for item, cnt in single_counts.items():
        if cnt >= min_support:
            L1[frozenset((item,))] = cnt 
    timing['L_times'][1] = time.perf_counter() - t_L1_start

    frequent = {}
    f1 = {}
    for kset, v in L1.items(): 
        f1[tuple(sorted(list(kset)))] = v 
    frequent[1] = f1
    prev_L = list(L1.keys())

    k = 1
    while prev_L: 
        k += 1

        t_Ck_start = time.perf_counter()
        Ck = candidate_gen(prev_L, k) 
        timing['C_times'][k] = time.perf_counter() - t_Ck_start

        if not Ck: 
            break

        t_Lk_start = time.perf_counter()
        Ck_counts = count_candidates(path, Ck)
        Lk = [] 
        for c, cnt in Ck_counts.items():
            if cnt >= min_support:
                Lk.append(c)
        timing['L_times'][k] = time.perf_counter() - t_Lk_start

        if not Lk:
            break
        fk = {} 
        for c in Lk: 
            fk[tuple(sorted(list(c)))] = Ck_counts[c]
        frequent[k] = fk
        prev_L = Lk
    return frequent, timing


