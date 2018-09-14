import os
import csv
import pandas as pd

def evaluate_performance(top_dir_originals, dir_generated, keys_originals, keys_generated, outdir):
    dir_originals = top_dir_originals+'cont_true_csv/'
    for csv_file in os.listdir(dir_originals):
        print(csv_file)
        if not csv_file.startswith('.'):
            with open(dir_originals+csv_file) as f:
                r = csv.DictReader(f, keys_originals)
                original = list(r)
            with open(dir_generated+csv_file) as f:
                r = csv.DictReader(f, keys_generated)
                generated = list(r)
            with open(top_dir_originals+'prime_csv/'+csv_file) as f:
                r = csv.DictReader(f, keys_originals)
                last_event_prime = list(r)[-1]
            outputlist = evaluate_continuation(original, generated, last_event_prime)
            outdf = pd.DataFrame(outputlist)
            outdf.to_csv(outdir+csv_file)

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
                    float(o['onset']) - float(last_event_prime['onset']), 2
                ) for o in original_events
            ]
            generated_iois = [
                round(
                    float(g['onset']) - float(last_event_prime['onset']), 2
                ) for g in generated_events
            ]
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
                'onset': onset,
                'pitches_correct': correct_pitches_at_n,
                'iois_correct': correct_iois_at_n,
                'pitch_ioi_pairs_correct': correct_pairs_at_n,
                'no_predicted_events': len(original_events),
                'prec_pitch': correct_pitches_at_n / len(generated_events),
                'prec_ioi': correct_iois_at_n / len(generated_events),
                'prec_pairs': correct_pitches_at_n / len(generated_events),
                'rec_pitch': correct_pitches_at_n / len(original_events),
                'rec_ioi': correct_pitches_at_n / len(original_events),
                'rec_pairs': correct_pitches_at_n / len(original_events)
            })
    return outputlist
