import random
import itertools


class S(object):
    def __init__(self, *args, **kwargs):
        if 'arguments' in kwargs:
            args = kwargs['arguments']
        self.weighted_options = args

    def choose(self):
        weights, options = zip(*self.weighted_options)
        choice = weighted_choice(options, weights)
        if isinstance(choice, S):
            return choice.choose()
        return choice


def frange(x, y, step=1.0):
    if step > 0:
        while x < y:
            yield x
            x += step
    if step < 0:
        while x > y:
            yield x
            x += step


def scale(x, minimum, maximum, floor=0, ceiling=1):
    return ((ceiling - floor) * (float(x) - minimum)) / (maximum - minimum) + floor


def weighted_choice(options, weights):
    rand = random.random()
    rand = scale(rand, 0, 1, 0, sum(weights))
    total = 0
    for i, weight in enumerate(weights):
        total += weight
        if rand < total:
            return options[i]


def set_start_end(notes):
    offset = 0
    for note in notes:
        note['start'] = offset
        note['end'] = offset + note['duration']
        offset += note['duration']


def get_at(offset, notes):
    for note in notes:
        if note['start'] <= offset < note['end']:
            return note


def pairwise(iterable):
    """
    >>> list(pairwise(range(5)))
    [(0, 1), (1, 2), (2, 3), (3, 4)]

    """
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)


def build_chord_type_on_root(root, chord_type):
    """
    >>> build_chord_type_on_root(9, [4, 3, 5])
    [9, 1, 4]

    """
    chord = [root]
    for interval in chord_type[:-1]:
        chord.append((chord[-1] + interval) % 12)
    return chord


def build_chord_type_on_all_roots(chord_type):
    """
    >>> build_chord_type_on_all_roots([4, 3, 5])
    [[0, 4, 7],
     [1, 5, 8],
     [2, 6, 9],
     [3, 7, 10],
     [4, 8, 11],
     [5, 9, 0],
     [6, 10, 1],
     [7, 11, 2],
     [8, 0, 3],
     [9, 1, 4],
     [10, 2, 5],
     [11, 3, 6]]

    """
    return [build_chord_type_on_root(root, chord_type) for root in range(12)]


def pitches_to_intervals(chord):
    """
    >>> pitches_to_intervals([12, 16, 31])
    [4, 3, 5]
    """
    # TODO rewrite this
    pcs = sorted(list(set([p % 12 for p in chord])))
    pcs = [p - pcs[0] for p in pcs]
    pcs.reverse()
    pcs.insert(0, 12)
    intervals = []
    for a, b in pairwise(pcs):
        intervals.append(a - b)
    intervals.reverse()
    return intervals
