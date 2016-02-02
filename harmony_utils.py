def zero(root, chord):
    """Give the pitch classes of `chord` as if `root` was 0."""
    return tuple(sorted([(p - root) % 12 for p in chord]))


def get_all_transpositions(chord):
    return list(set([zero(p, chord) for p in chord]))


allowed_chord_types = [
    # Feb3 chord types + Billboard/McGill chord types that happen > 1 in 1000
    # Preferring original Feb3 order, with a little manual reordering
    (0, 4, 7),
    (0, 3, 7),
    (0,),
    (0, 5),
    (0, 4),
    (0, 5, 7),
    (0, 3),
    (0, 4, 7, 10),
    (0, 3, 5),
    (0, 2),
    (0, 2, 5),
    (0, 3, 7, 10),
    (0, 2, 4, 7),
    (0, 3, 5, 7),
    (0, 2, 5, 7),
    (0, 2, 4, 7, 9),
    (0, 4, 7, 11),
    (0, 2, 4, 7, 10),
    (0, 3, 7, 9),
    (0, 2, 4),
    (0, 2, 6),
    (0, 3, 4, 7, 10),
    (0, 4, 7, 9),
    (0, 2, 3, 7, 10),
    (0, 5, 7, 10),
    (0, 2, 5, 7, 10),
    (0, 2, 4, 7, 11),
    (0, 2, 4, 5, 7, 10),
    (0, 4, 5, 7),
    (0, 2, 4, 5, 7, 9, 10),
    (0, 7, 10),
    (0, 2, 3, 5, 7, 10),
    (0, 2, 7),
    (0, 3, 6, 10),
    (0, 3, 6),
    (0, 3, 5, 7, 10),
    (0, 2, 3, 7),
    (0, 4, 8),

    # Feb3 chord types + Billboard/McGill chord types that happen > 1 in 1000
    # (0, 4, 7),
    # (0, 3, 7),
    # (0, 4, 7, 10),
    # (0, 3, 7, 10),
    # (0, 4, 7, 11),
    # (0, 5),
    # (0, 2, 4, 7),
    # (0,),
    # (0, 3, 4, 7, 10),
    # (0, 5, 7),
    # (0, 4, 7, 9),
    # (0, 2, 3, 7, 10),
    # (0, 5, 7, 10),
    # (0, 2, 5, 7, 10),
    # (0, 2, 4, 7, 11),
    # (0, 2, 4, 5, 7, 10),
    # (0, 2, 4, 7, 10),
    # (0, 3, 7, 9),
    # (0, 4, 5, 7),
    # (0, 2, 4, 5, 7, 9, 10),
    # (0, 2, 4, 7, 9),
    # (0, 7, 10),
    # (0, 2, 3, 5, 7, 10),
    # (0, 3, 5, 7),
    # (0, 2, 7),
    # (0, 3, 6, 10),
    # (0, 3, 6),
    # (0, 3, 5, 7, 10),
    # (0, 2, 5, 7),
    # (0, 2, 3, 7),
    # (0, 4, 8),
    # (0, 2, 4),
    # (0, 4),
    # (0, 2, 5),
    # (0, 3),
    # (0, 3, 5),
    # (0, 2),
    # (0, 2, 6),

    # Original Feb3 chordtypes
    # (0,),
    # (0, 5),
    # (0, 4),
    # (0, 4, 7),
    # (0, 3, 7),
    # (0, 3),
    # (0, 5, 7),
    # (0, 3, 5),
    # (0, 2),
    # (0, 2, 5),
    # (0, 3, 7, 10),
    # (0, 4, 7, 10),
    # (0, 2, 4, 7),
    # (0, 3, 5, 7),
    # (0, 2, 5, 7),
    # (0, 2, 4, 7, 9),
    # (0, 4, 7, 11),
    # (0, 2, 4, 7, 10),
    # (0, 3, 7, 9),
    # (0, 2, 4),
    # (0, 2, 6),
    # (0, 3, 6),
    # (0, 4, 8)

    # Billboard / McGill chord types
    # (0, 2, 3, 7, 9),
    # (0, 4, 7, 9, 11),
    # (0, 7),
    # (0, 5, 7),
    # (0, 4, 6, 7, 11),
    # (0, 10),
    # (0, 4, 5, 7, 9),
    # (0, 7, 10),
    # (0, 3, 4, 7, 10),
    # (0, 7, 8),
    # (0, 2, 5, 7, 9, 10),
    # (0, 2, 5),
    # (0, 4, 8),
    # (0, 2, 7),
    # (0, 4, 7, 9, 10),
    # (0, 3, 7, 8, 10),
    # (0,),
    # (0, 3, 6, 9),
    # (0, 4, 6, 7),
    # (0, 3, 6, 10),
    # (0, 4, 6, 10),
    # (0, 1, 3, 6),
    # (0, 1, 4, 7, 10),
    # (0, 3, 5, 7),
    # (0, 2, 3, 7, 11),
    # (0, 2, 4, 8, 10),
    # (0, 4, 6, 7, 9),
    # (0, 4, 7, 11),
    # (0, 5, 7, 8, 10),
    # (0, 5, 7, 11),
    # (0, 4, 7, 8),
    # (0, 4, 5, 7, 11),
    # (0, 3, 7, 9),
    # (0, 2, 4, 7, 10),
    # (0, 1, 4, 7, 9),
    # (0, 2, 3, 7, 8, 10),
    # (0, 2, 3, 5, 7, 10),
    # (0, 3, 7, 8),
    # (0, 3, 7, 11),
    # (0, 5),
    # (0, 2, 4, 6, 7),
    # (0, 3, 7, 9, 10),
    # (0, 8),
    # (0, 3, 7),
    # (0, 2, 3, 7, 10),
    # (0, 2, 5, 7),
    # (0, 4, 5, 7, 10),
    # (0, 2, 5, 7, 11),
    # (0, 4, 7, 10, 11),
    # (0, 5, 6),
    # (0, 2, 4, 7, 11),
    # (0, 3, 5, 7, 10),
    # (0, 3, 6, 11),
    # (0, 4, 11),
    # (0, 3, 7, 9, 11),
    # (0, 4, 6, 7, 9, 11),
    # (0, 3, 5, 6, 10),
    # (0, 2, 5, 6, 7, 10),
    # (0, 7, 9),
    # (0, 2, 4, 6, 7, 11),
    # (0, 2, 4),
    # (0, 4, 8, 11),
    # (0, 2, 5, 7, 10),
    # (0, 2, 6, 7),
    # (0, 4),
    # (0, 2, 4, 8),
    # (0, 2, 4, 6, 7, 10),
    # (0, 2, 4, 5, 7, 9, 11),
    # (0, 4, 7, 9),
    # (0, 4, 5, 7, 9, 10),
    # (0, 2, 3, 5, 10),
    # (0, 4, 7, 8, 10),
    # (0, 3, 5, 7, 11),
    # (0, 4, 5, 7),
    # (0, 1, 3, 7, 10),
    # (0, 1, 4, 7),
    # (0, 1, 4, 5, 7, 10),
    # (0, 2, 4, 6, 7, 9, 10),
    # (0, 3, 7, 10),
    # (0, 4, 7),
    # (0, 9),
    # (0, 2, 4, 7, 9, 10),
    # (0, 3, 10),
    # (0, 2, 4, 7, 8, 10),
    # (0, 2, 7, 10),
    # (0, 2, 4, 7, 9, 11),
    # (0, 3),
    # (0, 2, 4, 7, 9),
    # (0, 2, 3, 5, 7),
    # (0, 2, 3, 6, 9),
    # (0, 4, 7, 8, 11),
    # (0, 2, 3, 7),
    # (0, 3, 4, 7, 11),
    # (0, 2, 3, 5, 7, 9, 10),
    # (0, 3, 6, 8),
    # (0, 3, 4, 7),
    # (0, 4, 6, 7, 10),
    # (0, 3, 6, 7, 9),
    # (0, 2, 4, 5, 7, 10),
    # (0, 2, 4, 5, 7, 9, 10),
    # (0, 3, 4, 7, 8, 10),
    # (0, 3, 6),
    # (0, 1, 4, 7, 8, 10),
    # (0, 2, 4, 7),
    # (0, 2, 4, 5, 7, 11),
    # (0, 1, 4, 6, 7, 10),
    # (0, 4, 8, 10),
    # (0, 2, 4, 6, 7, 9, 11),
    # (0, 5, 7, 10),
    # (0, 4, 7, 10)
]
allowed_chord_types_transpositions = []
for c in allowed_chord_types:
    allowed_chord_types_transpositions.extend(get_all_transpositions(c))
allowed_chord_types_transpositions.append(())


def is_allowed(chord):
    if not chord:
        return True
    return zero(chord[0], chord) in allowed_chord_types_transpositions


def find_supersets(subset, chord_type):
    supersets = []
    chord_type = list(chord_type)
    for offset in subset:
        for i, root in enumerate(chord_type):
            transposition = chord_type[i:] + chord_type[:i]
            transposition = tuple(sorted([(p - root + offset) % 12 for p in transposition]))
            if all([(p in transposition) for p in subset]):
                if transposition not in supersets:
                    supersets.append(transposition)
    return supersets


def find_all_supersets(subset):
    supersets = []
    for chord_type in allowed_chord_types:
        supersets.extend(find_supersets(subset, chord_type))
    return supersets
