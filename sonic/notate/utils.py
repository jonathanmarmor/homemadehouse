import itertools


def frange(x, y, step=1.0):
    if step > 0:
        while x < y:
            yield x
            x += step
    if step < 0:
        while x > y:
            yield x
            x += step


def split_at_offsets(dur, offsets):
    """split a single duration at offsets."""
    if len(offsets) == 0:
        return [dur]

    components = []
    offsets.append(dur)
    start = 0
    for offset in offsets:
        components.append(offset - start)
        start = offset

    return components


def split_at_beats(note_durs):
    """Split a list of durations at quarter notes."""
    beat_indexes = list(frange(0, sum(note_durs)))

    total = 0
    components = []
    for dur in note_durs:
        start = total
        end = total + dur

        split_at = []
        for beat in beat_indexes:
            if start < beat < end:
                split_point = beat - start
                split_at.append(split_point)

        note_components = split_at_offsets(dur, split_at)
        components.append(note_components)
        total += dur

    return components


def join_quarters(dur_components):
    """For duration components of a single note, join together any adjacent quarter note components

    >>> join_quarters([1.0, 1.0])
    [2.0]
    >>> join_quarters([1.0, 1.0, 0.5])
    [2.0, 0.5]
    >>> join_quarters([.25, .25])
    [0.25, 0.25]
    >>> join_quarters([1.0, .25, .25])
    [1.0, 0.25, 0.25]

    """
    if 1.0 not in dur_components:
        return dur_components
    new_durs = []
    for key, group in itertools.groupby(dur_components):
        if key == 1.0:
            group = [sum(group)]
        new_durs.extend(group)

    return new_durs


def join_rests(music):
    """Find consecutive notes that are rests and join them into one rest with the full duration"""
    result = []
    for is_rest, notes in itertools.groupby(music, lambda x: x.get('pitch') == 'rest'):
        if is_rest:
            duration = sum(n['duration'] for n in notes)
            note = {
                'pitch': 'rest',
                'duration': duration
            }
            result.append(note)
        else:
            result.extend(notes)
    return result


# Unused
# def group_into_bars(notes):
#     bars = []
#     bar = []
#     total = 0
#     for note in notes:
#         bar.append(note)

#         total += note['duration']

#         if total > 4:
#             raise Exception('Ties over barlines arent allowed yet. Sorry.')

#         if total == 4:
#             bars.append(bar)
#             bar = []
#             total = 0

#     if len(notes) != sum([len([n for n in b]) for b in bars]):
#         raise Exception('The number of notes in the input is not the same as the number of notes in the output. Input: {} Output: {}.'.format(notes, bars))

#     return bars


if __name__ == '__main__':
    import doctest
    doctest.testmod()
