from typing import Iterable
from itertools import combinations
from math import isclose

class AssociationRules:
    """
    Generate association rules from a set of frequent itemsets.

    Definitions (from the book):
    ----------------------------
    Let T be the set of all transactions, |T| = N

    - Support of an itemset X:
        support(x) = |{ t in T : X subset of t }| / N  (fraction in [0, 1])

    - Confidence of rule X -> Y:
        conf(X -> Y) = support(X U Y) / support(X)

    Inputs:
    ----------
    frequent_itemsets: dict mapping frozenset -> support_count (absolute)
    n_transactions: total number of transactions in the dataset
    min_support : minimum support threshold (fraction in [0, 1])
    min_confidence : minimum confidence threshold (fraction in [0, 1])

    Example:
    --------
    Suppose we have frequent_itemsets with counts:
        {A}: 3, {B}: 3, {A, B}: 2, N = 4 transactions.

    Then:
        support({A}) = 3/4 = 0.75
        support({B}) = 3/4 = 0.75
        support({A,B}) = 2/4 = 0.5

    The rule A -> B has:
        conf = support({A,B}) / support({A}) = 0.5 / 0.75 = 0.667
    """
    def __init__(self, frequent_itemsets: dict[frozenset, int],
                 n_transactions: int,
                 min_support: float = 0.0,
                 min_confidence: float = 0.0):
        # Normalize keys to frozenset for consistent lookup
        self._support = {}
        n = float(n_transactions)
        for k, v in frequent_itemsets.items():
            # Convert key to frozenset (if it's already frozenset, this is a no-op)
            fs = frozenset(k) if not isinstance(k, frozenset) else k
            self._support[fs] = float(v) / n

        self.min_support = float(min_support)
        self.min_confidence = float(min_confidence)

    @staticmethod
    def _all_nonempty_proper_subsets(itemset: frozenset) -> Iterable[frozenset]:
        """
        Yield all non-empty proper subsets of a given itemset.
        For itemset size n, yields subsets of sizes 1 .. n-1.

        Example:
        --------
        itemset = {A, B, C}
        yields: {A}, {B}, {C}, {A, B}, {A, C}, {B, C}
        """
        items = list(itemset)
        n = len(items)
        # sizes 1 .. n-1
        for r in range(1, n):
            for comb in combinations(items, r):
                yield frozenset(comb)

    def generate_rules(self) -> list[dict[str, object]]:
        """
        Generate association rules satisfying min_support and min_confidence.

        For each frequent itemset I with |I| >= 2:
            - Consider all non-empty proper subsets LHS.
            - RHS = I \ LHS
            - Rule: LHS -> RHS
            - Compute support(I), support(LHS), support(RHS)
            - Compute confidence (LHS -> RHS)
            - Keep rule if:
                support(I) >= min_support
                confidence >= min_confidence

        Returns:
        -------
        List of rules, each as a dict
            {
                'lhs': frozenset of antecedent items
                'rhs': frozenset of consequent items
                'support': support of lhs U rhs (float)
                'confidence': confidence of the rule (float)
            }
        """
        rules = []
        # Iterate through all frequent itemsets with size >= 2
        for itemset, sup_itemset in self._support.items():
            if len(itemset) < 2:
                continue
            # Check support threshold for the full itemset
            if sup_itemset + 1e-12 < self.min_support:
                continue

            # For every non-empty proper subset LHS, form rule LHS -> RHS
            for lhs in self._all_nonempty_proper_subsets(itemset):
                rhs = itemset - lhs
                if not rhs:
                    continue  # RHS must be non-empty

                sup_lhs = self._support.get(lhs)
                # If lhs is not in the provided frequent_itemsets mapping, we cannot compute confidence reliably; skip such cases.
                if sup_lhs is None or isclose(sup_lhs, 0.0):
                    continue

                confidence = sup_itemset / sup_lhs
                if confidence + 1e-12 < self.min_confidence:
                    continue

                rule = {
                    'lhs': lhs,
                    'rhs': rhs,
                    'support': sup_itemset,
                    'confidence': confidence,
                }
                rules.append(rule)

        # Sort rules by confidence (descending), then support
        rules.sort(key=lambda r: (r['confidence'], r['support']), reverse=True)
        return rules
