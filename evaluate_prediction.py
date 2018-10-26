
def evaluate_continuation(original, generated, last_event_prime, evaluate_until_onset=10.0):
    """ Given the original and the generated continuation
    of the test item (in onset/pitch dictionaries),
    collect the following events (which can be mulitple pitches),
    and determine how many pitches / iois and pitch/ioi pairs are shared between 
    generated and original piece.
    For the first ioi, the last event of the prime is also required.
    'evaluate_until_onset determines' until how many quarter notes 
    after the cut-off point we evaluate.
    Output is a list of dictionaries, 
    in which the key indicates the onsets after cut-off
    for which correct number of pitches, iois and pitch/ioi pairs are listed. 
    """

    original_onsets = sorted(list(set([float(o['onset']) for o in original])))
    generated_onsets = sorted(list(set([float(g['onset']) for g in generated])))
    outputlist = []
    max_onset = original_onsets[0] + evaluate_until_onset
    for onset in original_onsets:
        if onset <= max_onset:
            original_events = [o for o in original if float(o['onset']) <= onset]
            generated_events = [
                g for g in generated if float(g['onset']) <= onset
            ]
            if not generated_events:
                continue
            original_pitches = [int(o['pitch']) for o in original_events]
            generated_pitches = [int(g['pitch']) for g in generated_events]
            original_iois = [
                round(
                    float(o['onset']) - float(original_events[i-1]['onset']), 2
                ) for i, o in enumerate(original_events)
            ]
            original_iois[0] = round(
                float(original_events[0]['onset']) - 
                float(last_event_prime['onset']), 2
            )
            generated_iois = [
                round(
                    float(o['onset']) - float(generated_events[i-1]['onset']), 2
                ) for i, o in enumerate(generated_events)
            ]
            generated_iois[0] = round(
                float(generated_events[0]['onset']) - 
                float(last_event_prime['onset']), 2
            )
            original_pairs = list(zip(original_pitches, original_iois))
            generated_pairs = list(zip(generated_pitches, generated_iois))
            correct_pitches_at_n = 0
            correct_iois_at_n = 0
            correct_pairs_at_n = 0
            for event in generated_pitches:
                if event in original_pitches:
                    correct_pitches_at_n += 1
                    original_pitches.pop(original_pitches.index(event))
            for event in generated_iois:
                if event in original_iois:
                    correct_iois_at_n += 1
                    original_iois.pop(original_iois.index(event))
            for event in generated_pairs:
                if event in original_pairs:
                    correct_pairs_at_n += 1
                    original_pairs.pop(original_pairs.index(event))
            outputlist.append({
                onset: {
                    'pitches_correct': correct_pitches_at_n,
                    'iois_correct': correct_iois_at_n,
                    'pitch_duration_pairs_correct': correct_pairs_at_n,
                    'no_predicted_events': len(original_events)
                }
            })
    return outputlist