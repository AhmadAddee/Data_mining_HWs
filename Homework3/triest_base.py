import random
from collections import defaultdict


class TriestBase:
    """
    TRIÈST-BASE algorithm (insertion-only graph stream).

    To maintain:
    - A reservoir sample of edges S (max size M).
    - Adjacency list of the sample graph.
    - Global triangle counter.

    At any time t, this can be done:
        - estimate_global()
    """

    def __init__(self, M: int):
        self.M = M     # reservoir capacity
        self.S: set[tuple[int, int]] = set()        # sampled edges
        self.adj: dict[int, set[int]] = defaultdict(set)    # adjacency in sample graph

        self.t_counter = 0 # global triangle counter
        self.t = 0 # Number of edges seen so far

        self._edges_list: list[tuple[int, int]] = []
        self._edges_pos: dict[tuple[int, int], int] = {}

    def process_edges(self, u: int, v: int) -> None:
        """
        Process one edge (u, v) coming from the stream.
        In TRIÈST-BASE, we assume insertion-only (no deletions).
        """
        if u == v:
            return
        if u > v:
            u, v = v, u

        self.t += 1 # one more edge seen
        t = self.t

        # Decide if this edge should be in the sample
        if self._sample_edge(u, v, t):
            # This edge is now in S, so we update the triangle counters
            self._update_counters(sign='+', u=u, v=v)

    def _sample_edge(self, u: int, v: int, t: int) -> bool:
        """
        Decide whether to keep (u, v) in the reservoir sample S.

        Returns True if the edge is inserted into S (possibly causing the removal of another edge), False otherwise.
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
            old_edge = self._edges_list[idx]
            ru, rv = old_edge

            # Before removing, adjust triangle counters
            self._update_counters(sign='-', u=ru, v=rv)
            self._remove_edge_from_sample_by_index(idx)

            # Insert the new edge
            self._insert_edge_in_sample(edge)
            return True

        # Edge not sampled
        return False

    def _insert_edge_in_sample(self, edge: tuple[int, int]) -> None:
        """Insert an edge into the reservoir and adjacency structure."""
        u, v = edge

        self.S.add(edge)

        self.adj[u].add(v)
        self.adj[v].add(u)

        idx = len(self._edges_list)
        self._edges_list.append(edge)
        self._edges_pos[edge] = idx

    def _remove_edge_from_sample_by_index(self, idx: int) -> None:
        """Remove an edge from S and adjacency structure."""
        last_idx = len(self._edges_list) - 1
        edge_to_remove = self._edges_list[idx]
        u, v = edge_to_remove

        self.S.discard(edge_to_remove)

        self.adj[u].discard(v)
        self.adj[v].discard(u)
        if not self.adj[u]:
            del self.adj[u]
        if not self.adj[v]:
            del self.adj[v]

        del self._edges_pos[edge_to_remove]

        if idx != last_idx:
            last_edge = self._edges_list[last_idx]
            self._edges_list[idx] = last_edge
            self._edges_pos[last_edge] = idx
        self._edges_list.pop()

    def _update_counters(self, sign: str, u: int, v: int) -> None:
        """
        Update global triangle counters when edge (u, v) is added or removed from the sample.

        Steps:
            1. Find shared neighbors C = N_S(u) ∩ N_S(v).
            2. For each c in C:
                - t_counter += 1 (or -= 1)
        """
        # Neighbors in the sample (default to an empty set if not present)
        neighbors_u = self.adj.get(u, set())
        neighbors_v = self.adj.get(v, set())
        shared = neighbors_u.intersection(neighbors_v)
        if not shared:
            # No triangles involving this edge
            return

        delta = 1 if sign == '+' else -1

        # Update global counter
        self.t_counter += delta * len(shared)

    def estimate_global(self) -> float:
        """
        Return current estimate of total number of triangles.
        """
        if self.t <= self.M:
            # Early phase: reservoir holds all edges, counts are exact
            return float(self.t_counter)
        else:
            xi = self._xi(self.t)
            return xi * self.t_counter

    @property
    def sample_size(self) -> int:
        """Current number of edges in the reservoir."""
        return len(self.S)

    def _xi(self, t:int) -> float:
        """
        Scaling factor xi(t) = max{1, [t(t-1)(t-2)] / [M(M-1)(M-2)]}.
        """
        if t < 3 or self.M < 3:
            return 1.0
        num = t * (t - 1) * (t - 2)
        den = self.M * (self.M - 1) * (self.M - 2)
        if den == 0:
            return 1.0
        return max(1.0, num / den)
