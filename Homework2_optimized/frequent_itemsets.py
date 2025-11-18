from collections import Counter
from itertools import combinations

class Apriori:
    """Simple implementation of the Apriori algorithm for mining frequent itemsets.

    Terminology:
    -----------
    - Transactions: a set of items bought together, e.g. {bread, milk}.
    - Itemset: any st of items, e.g. {bread}, {bread, milk}, etc.
    - Support of an itemset: number of transactions that contain all items in the set

    Input:
    -----
    - transactions: list of transactions, each is a frozenset of items (str, int, ...).
    - min_support: minimum support threshold (absolute count).

    Output:
    ------
    - A dict mapping frozenset(itemset) -> support_count (int) for all frequent itemsets.

    Example:
    --------
    transactions = [
        frozenset(["A", "C", "D"]),
        frozenset(["B", "C", "E"]),
        frozenset(["A", "B", "C", "E"]),
        frozenset(["B", "E"])
    ]
    if min_support = 2, some frequent itemsets will be:
    {c} with support 3
    {B, E} with support 3
    {B, C} with support 2
    ...
    """

    @staticmethod
    def _gen_candidates(prev_frequents: list[frozenset], k: int) -> list[frozenset]:
        """
        Generate candidate k-itemsets (c_k) from frequent (k-1)-itemsets (L_{k-1}).

        Two (k-1)-itemsets are joined if they share the first k-2 items (in stored order).

        Example:
        --------
        Suppose L2 = { {A, B}, {A, C}, {B, C} }.
        Then the candidates C3 will include {A, B, C}.
        """
        prev_list = list(prev_frequents)
        candidates = set()
        m = len(prev_list)
        for i in range(m):
            for j in range(i + 1, m):
                union = prev_list[i] | prev_list[j]
                if len(union) == k:
                    candidates.add(frozenset(union))
        return list(candidates)

    @staticmethod
    def _prune_candidates(candidates, prev_frequent_set, k: int) -> list[frozenset]:
        """
        Prune candidates using the Apriori principle:

        If a candidate k-itemset has any (k-1)-subset that is NOT frequent, then the candidate itself cannot be
        frequent and is removed.

        Example:
        --------
        Suppose candidate {A, B, C} and k=3.
        We check all 2-subsets: {A, B}, {A, C}, {B, C}.
        If any of these is not in L2 (prev_frequent_set), we drop {A, B, C}.
        """
        pruned = []
        for c in candidates:
            all_subset_frequent = True
            # all (k-1)-subsets of this candidate
            for subset in combinations(c, k-1):
                if frozenset(subset) not in prev_frequent_set:
                    all_subset_frequent = False
                    break
            if all_subset_frequent:
                pruned.append(c)
        return pruned

    @staticmethod
    def _count_support(transactions: list[frozenset], candidates: list[frozenset], k: int, min_support: int) -> dict[frozenset, int]:
        """
        count supports for candidates k-itemsets.

        Optimization:
        ------------
        Instead of, for each transaction, checking "is candidate subset of transaction?" for *all* candidates, we:
            - For each transaction T, generate all k-subsets S of T.
            - Only if S is in the candidate set, we increment its count.

        This reduces the number of subset checks dramatically when there are many candidates but transactions are
        relatively short.

        Complexity (roughly):
        ---------------------
        O ( sum_over_transactions C(|T|, k) instead of O ( |transactions| * |candidates| * k)
        """
        counts = Counter()
        candidate_set = set(candidates)

        for t in transactions:
            if len(t) < k:
                # Transaction too small to contain any k-itemset
                continue
            # Generate all k-subsets of this transaction
            for comb in combinations(t, k):
                subset = frozenset(comb)
                if subset in candidate_set:
                    counts[subset] += 1

        # Keep only those that reach min_support
        frequent_k = {c: cnt for c, cnt in counts.items() if cnt >= min_support}
        return frequent_k

    def get_frequent_count(self, transactions: list[frozenset], min_support: int):
        """
        Run the Apriori algorithm and return all frequent itemsets (with counts).

        Steps:
        ------
        1. Find frequent 1-itemsets L1.
        2. For k = 2, 3, ....:
            a) Generate candidates c_k = join(L_{k-1}, L_{k-1})
            b) Prune candidates using Apriori principle
            c) Count support for c_k
            d) Keep those >= min_support as L_k
            e) Stop when L_k is empty.
        """
        if not transactions:
            return {}

        # Step 1: find frequent 1-itemsets (L1)
        item_counts = Counter()
        for t in transactions:
            for item in t:
                item_counts[item] += 1

        frequent_itemsets = {}
        L1 = set()
        for item, cnt in item_counts.items():
            if cnt >= min_support:
                fs = frozenset([item])
                L1.add(fs)
                frequent_itemsets[fs] = cnt

        # Step 2: iteratively build L2, L3, ....
        k = 2
        prev_L = L1
        while prev_L:
            # 2a. Generate candidate k-itemsets from L_{k-1}
            candidates = self._gen_candidates(prev_L, k)
            if not candidates:
                break
            # 2.b Prune candidates
            candidates = self._prune_candidates(candidates, prev_L, k)
            if not candidates:
                break
            # 2.c Count support for candidates in the dataset
            frequent_k = self._count_support(transactions, candidates, k, min_support)
            # 2.d If no frequent k-itemsets, stop
            if not frequent_k:
                break
            prev_L = set(frequent_k.keys())
            frequent_itemsets.update(frequent_k)
            k += 1

        return frequent_itemsets
