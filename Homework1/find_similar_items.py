from __future__ import annotations
from collections import defaultdict
import hashlib
import random
from dataclasses import dataclass

# Task 1: Shingling
@dataclass
class Shingling:
    k: int = 10

    def shingles(self, text: str, use_hashing=True) -> list[int | str]:
        """construct k-shingles of a given length k (default 10) from a given document.
        if you use_hashing, it computes a hash value for each unique shingle and represents the
        document in the form of an ordered set of its hashed k-shingles.

        Args:
            text (str): The input document to be shingled.
            use_hashing (bool): default True, and determines wither to hash the shingles.
        Returns:
            list: An ordered set of the (hashed/char) k-shingles.
        """
        shingle_set = set()
        for i in range(len(text) - self.k + 1):
            shingle = text[i : i + self.k]
            # Compute a hash value of it if desired
            if use_hashing:
                shingle = int(hashlib.md5(shingle.encode("utf-8")).hexdigest(), 16) % (2**32)
            shingle_set.add(shingle)
        return sorted(shingle_set)


# Task 2: CompareSets: Jaccard on sets of hashed shingles
class CompareSets:

    @staticmethod
    def jaccard(a: set[int]|list[int], b: set[int]|list[int]) -> float:
        """computes the Jaccard similarity of two integer sets - two sets of hashed shingles.

        Args:
            a (set | list): The first input set of hashed shingles.
            b (set | list): The first input set of hashed shingles.
        Returns:
            float: A float value between 0-1 representing the Jaccard similarity between the two shingle sets.
        """
        a = set(a)
        b = set(b)
        intersection = a.intersection(b)
        union = a.union(b)
        return len(intersection) / len(union) if union != 0 else 0


# Task 3: MinHashing
@dataclass
class MinHashing:
    signature_len: int = 100
    # The first prime number coming after 2^32 (larger than any possible hashed shingle).
    P: int = 4294967311

    def __post_init__(self):
        # Can be removed, but to have reproducibility for each run of the hashing.
        rand = random.Random(42)
        self.a = [rand.randrange(1, self.P -1) for _ in range(self.signature_len)]
        self.b = [rand.randrange(0, self.P -1) for _ in range(self.signature_len)]

    def get_signature(self, hashed_set: list) -> list[int]:
        """builds a minHash signature (in the form of a list) of a given length n
        from a given set of integers (a set of hashed shingles).

        Args:
            hashed_set (list): The set of hashed shingles.
        Returns:
            list: A list of length signature_len representing the Min-hash vector of the shingle set.
        """
        signatures = [self.P] * self.signature_len

        # h(x) = (ax + b) mod p
        for x in hashed_set:
            for i in range(self.signature_len):
                hash_value = (self.a[i] * x + self.b[i]) % self.P
                if hash_value < signatures[i]:
                    signatures[i] = hash_value
        return signatures


# Task 4: Compare signatures
class CompareSignatures:
    @staticmethod
    def estimate(signature1: list[int], signature2: list[int]) -> float:
        """estimates the similarity f two integer lists - minhash signatures - as a fraction
        of components in which they agree.

        Args:
            signature1 (list): the first min-hashed-based (integer) signature.
            signature2 (list): the second min-hashed-based (integer) signature.
        Returns:
            float: representing the fraction of the components where they are equal.
        """
        if not len(signature1) == len(signature2):
            raise Exception("Signatures must have same length")

        matches = sum(1 for a, b in zip(signature1, signature2) if a == b)
        return matches / len(signature1)


# Task 5: LSH banding
@dataclass
class LSH:
    bands: int

    def __post_init__(self):
        if self.bands <= 0:
            raise ValueError("bands must be >= 1")

    @staticmethod
    def choose_bands(signature_len: int, target_threshold: float) -> int:
        # signature_len = b * r (must be an integer)
        # S-curve threshold should be as close to the similarity as possible; s ~= target_threshold
        best_b, best_err = 1, 1
        for b in range(1, signature_len + 1):
            if signature_len % b != 0:
                continue
            r = signature_len // b
            s_curve_threshold = (1.0 / b) ** (1.0 / r)
            err = abs(s_curve_threshold - target_threshold)
            if err < best_err:
                best_b, best_err = b, err
        return best_b

    def candidate_pairs(self, signatures: dict[str, list[int]], t: float) -> set[tuple[str, str]]:
        """implements the LSH technique: given a collection of minhash signatures (integer vectors) and a similarity
        threshold t, the LSH class (using banding and hashing) finds candidate pairs of signatures agreeing on at least
        a fraction t of their components.

        Args:
            signatures (dict): the collection of min-hashed-based (integer) signatures.
            t (float): the similarity threshold that signatures must agree upon to be candidates.
        Returns:
            set: representing the candidate pairs of signatures to be similar.
        """
        if not signatures:
            return set()
        # All signatures must have same length and be divisible by bands
        keys = list(signatures.keys())
        siglen = len(signatures[keys[0]])
        if any(len(signatures[k]) != siglen for k in keys):
            raise ValueError("All signatures must have the same length")
        if siglen % self.bands != 0:
            raise ValueError("Signature length must be divisible by number of bands")
        r = siglen // self.bands

        # Step 1: hash each band to buckets
        buckets: list[dict[int, list[str]]] = [defaultdict(list) for _ in range(self.bands)]
        for doc_id, sig in signatures.items():
            for b in range(self.bands):
                start, end = b * r, (b + 1) * r
                band_tuple = tuple(sig[start:end])
                # Stable hash for the band tuple
                #h = stable_32bit_hash("|".join(map(str, band_tuple)))
                h = int(hashlib.md5("|".join(map(str, band_tuple)).encode("utf-8")).hexdigest(), 16) % (2**32)
                buckets[b][h].append(doc_id)

        # Step 2: generate candidate pairs (same bucket in any band)
        candidates: set[tuple[str, str]] = set()
        for b in range(self.bands):
            for _, ids in buckets[b].items():
                if len(ids) > 1:
                    ids_sorted = sorted(ids)
                    for i in range(len(ids_sorted)):
                        for j in range(i + 1, len(ids_sorted)):
                            candidates.add((ids_sorted[i], ids_sorted[j]))

        # Step 3: filter by signature agreement threshold (optional but useful)
        filtered: set[tuple[str, str]] = set()
        for a, b in candidates:
            sim = CompareSignatures.estimate(signatures[a], signatures[b])
            if sim >= t:
                filtered.add((a, b))
        return filtered
