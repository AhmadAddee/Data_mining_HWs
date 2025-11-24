import random

class ReservoirSampler:
    """
    Generic reservoir sampler that keeps a uniform random sample of size M from a stream of unknown length.

    Usage:
    ------
    rs = ReservoirSampler(M=100)
    for item in stream:
        rs.process(item)

    final_sample = rs.sample
    """

    def __init__(self, M: int):
        self.M = M      # Maximum sample size
        self.sample: list = []
        self.n_seen = 0

    def process(self, item) -> None:
        """Process one item from the stream."""
        self.n_seen += 1
        i = self.n_seen

        if i <= self.M:
            # Still filling the reservoir
            self.sample.append(item)
        # Decide whether to include this new item
        elif random.random() < (self.M / i):
            # Replace a random element in the reservoir
            j = random.randrange(self.M)    # index in [0, M-1]
            self.sample[j] = item