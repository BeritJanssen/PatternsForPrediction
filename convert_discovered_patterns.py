import numpy as np
from collections import Counter


def pattern_to_prediction(piece, pattern_output, n=20):
    """ Given a piece in onset/pitch representation and
    pattern output in a list of lists [patterns[occurrences]],
    find the pattern which matches the n notes of the piece
    before the cut-off point best.
    The following note from the pattern is picked as the predicted
    next event.
    """
    pre_cutoff = np.array(
        [(s['onset'], s['pitch']) for s in piece[:-n]]
    )
    all_matches = []
    for index, pattern in enumerate(pattern_output):
        # occurrences are translation equivalent, so picking first one
        translation_vectors = []
        compare_pattern = np.array(
            [(s['onset'], s['pitch']) for s in pattern[0]]
        )
        for point in compare_pattern:
            vectors = (pre_cutoff - point)
            translation_vectors.extend([tuple(v) for v in vectors])
        grouped_vectors = dict(Counter(translation_vectors))
        similarity = max([grouped_vectors[k] for k in grouped_vectors])
        shifts = [
            key for key in grouped_vectors if
            grouped_vectors[key] == similarity
        ]
        for shift in shifts:
            # check last relevant note of pattern, generate prediction
            last_note_pattern = next((
                i for i, p in enumerate(compare_pattern) if
                p+shift in pre_cutoff
            ), None)
            if last_note_pattern < (len(compare_pattern) - 1):
                prediction = compare_pattern[last_note_pattern+1]
        all_matches.append({
            'pattern_no': index,
            'similarity': similarity,
            'prediction': prediction
        })
    return all_matches
