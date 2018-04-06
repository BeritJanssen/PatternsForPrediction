
def evaluate_continuation(original, generated, n=40):
    """ Given the original and the generated continuation
    of the test item (in onset/pitch pairs),
    collect the following n events (which can be mulitple pitches),
    and determine how many pitches / iois are shared between 
    generated and original piece.
    n is the number at which we cut off the measure
    set to 40 by default as suggested by Tom 
    output is a list of dictionaries, in which n gives the cutoff point,
    for which correct number of pitches and iois are listed. 
    """

    original_onsets = sorted(list(set([o['onset'] for o in original])))
    generated_onsets = sorted(list(set([g['onset'] for g in generated])))
    outputlist = []

    for index, onset in enumerate(original_onsets):
        if index <= n:
            original_events = [o for o in original if o['onset'] <= onset]
            generated_events = [
                g for g in generated if g['onset'] <= generated_onsets[index]
            ]
            original_pitches = [o['pitch'] for o in original_events]
            generated_pitches = [g['pitch'] for g in generated_events]
            original_iois = [
                o['onset']-original_events[i-1]['onset']
                for i, o in enumerate(original_events)
            ]
            generated_iois = [
                g['onset']-generated_events[i-1]['onset']
                for g in generated_events
            ]
            correct_pitches_at_n = 0
            correct_iois_at_n = 0
            for event in generated_pitches:
                if event in original_pitches:
                    correct_pitches_at_n += 1
                    original_pitches.pop(original_pitches.index(event))
            for event in generated_iois:
                if event in original_iois:
                    correct_iois_at_n += 1
                    original_iois.pop(original_iois.index(event))
            outputlist.append(
                {'n': n, {
                    'pitches_correct': correct_pitches_at_n,
                    'iois_correct': correct_iois_at_n}})
    return outputlist