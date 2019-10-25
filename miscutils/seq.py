def split(i, seq):
    return seq[:i], seq[i:]


def inits(seq):
    return (seq[: i + 1] for i in range(len(seq)))


def tails(seq):
    return (seq[:i] for i in range(len(seq), 0, -1))
