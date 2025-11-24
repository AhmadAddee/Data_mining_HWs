import random
from collections import defaultdict
from triest_base import TriestBase


"""
What is the difference between TRIÈST-BASE and TRIÈST-IMPR presented in the paper?
TRIÈST-IMPR has the same idea, but with these three surgical changes:
    1. Update counters for every edge (not only stamped ones)
    2. Never decrement counters when removing edges from the reservoir.
    3. Use a weight n(t) inside UpdateCounters instead of the global scaling factor xi(t)
"""

class TriestImpr(TriestBase):
    """
    TRIÈST-IMPR (Improved Variant).

    Key differences from TriestBase (Algorithm 2 in the paper):

        1) UpdateCounters is called for *every* edge in the stream, BEFORE deciding whether it goes into the sampl
            (and we only ever "add", never "subtract").

        2) When an edge is evicted from the sample, we DO NOT decrement any counters.

        3) UpdateCounters uses a weight n(t) = max{1, (t-1)(t-2)/(M(M-1))}, and we do NOT use the global xi(t) scaling
            factor anymore. The estimator is just t(t_counter) directly.

    Intuition:
        - We "pretend" every edge could have contributed to triangles in the full graph, and we correct the under-
            sampling by multiplying with n(t), which comes from the probability that the other two edges of a triangle
            are in the sample at time t.
    """

    def __init__(self, M: int):
        # Reuse all data structures from TriestBase
        super().__init__(M)
        # For IMPR, t_counter will typically become a float (because of n)

    def process_edges(self, u: int, v: int) -> None:
        """
        IMPR variant:

        For each incoming edge (u, v):
            1) Increase time t.
            2) Call _update_counters(u, v) regardless of whether (u, v) will end up in the sample or not (this is the
                biggest conceptual change vs. BASE).
            3) Then call _sample_edge(...) to possibly modify the sample.

        Important: _sample_edge in IMPR does NOT touch counters when removing edges from the sample.
        """
        if u == v:
            return
        if u > v:
            u, v = v, u

        self.t += 1
        t = self.t

        # IMPR: always update counters first
        self._update_counters_impr(u, v)

        # Decide if this edge should be in the sample
        self._sample_edge_impr(u, v, t)

    def estimate_global(self) -> float:
        """
        IMPR estimator: the counter t(t) is *already* corrected via n(t), so we just return its value directly.
        """
        return float(self.t_counter)

    def _sample_edge_impr(self, u: int, v: int, t: int) -> bool:
        """
        IMPR reservoir sampling:

        STILL keeps a uniform random sample of up to M edges, but DOES NOT change triangle counters on removal.
        """
        edge = (u, v)

        # Ignore duplicates already in sample
        if edge in self.S:
            return False

        if len(self.S) <= self.M:
            # Still filling the reservoir
            self._insert_edge_in_sample(edge)
            return True

        # Reservoir is full: keep this edge with probability M/t
        if random.random() < self.M / t:
            # Choose one edge uniformly at random to remove
            idx = random.randrange(len(self.S))
            self._remove_edge_from_sample_by_index(idx)

            # Insert the new edge
            self._insert_edge_in_sample(edge)
            return True

        # Edge not sampled
        return False

    def _update_counters_impr(self, u: int, v: int) -> None:
        """
        IMPR version of UpdateCounters

        1) Compute shared neighbors C = N_S(u) ∩ N_S(v) in the current sample graph (before adding (u, v)).

        2) Compute weight n(t) = max{1, (t-1)(t-2) / (M(M-1))}.

        3) For each c in C, t += n.
        """
        neighbors_u = self.adj.get(u, set())
        neighbors_v = self.adj.get(v, set())
        shared = neighbors_u.intersection(neighbors_v)
        if not shared:
            # No triangles involving this edge
            return

        t = self.t
        if t <= 2 or self.M < 2:
            eta = 1.0
        else:
            eta = (t -1) * (t - 2) / (self.M * (self.M - 1))
            if eta < 1.0:
                eta = 1.0

        self.t_counter += eta * len(shared)
