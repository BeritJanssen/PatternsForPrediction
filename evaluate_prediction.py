import os
import csv
import pandas as pd
import numpy as np
from collections import Counter

def evaluate_performance(
    top_dir_originals, 
    dir_generated, 
    keys_originals, 
    keys_generated, 
    outdir, 
    algorithm,
    evaluation_method='list',
    onset_increment=1.0, 
    evaluate_until_onset=10.0):
    dir_originals = top_dir_originals+'cont_true_csv/'
    print(algorithm)
    complete_list = []
    for csv_file in os.listdir(dir_originals):
        print(csv_file)
        if not csv_file.startswith('.'):
            with open(dir_originals+csv_file) as f:
                r = csv.DictReader(f, keys_originals)
                original = list(r)
            generated_file = next((gen for gen in os.listdir(dir_generated) if gen.startswith(csv_file[:-4])), None)
            with open(dir_generated+generated_file) as f:
                r = csv.DictReader(f, keys_generated)
                generated = list(r)
            with open(top_dir_originals+'prime_csv/'+csv_file) as f:
                r = csv.DictReader(f, keys_originals)
                last_event_prime = list(r)[-1]
            outputlist = evaluate_continuation(original, generated, last_event_prime, evaluation_method, onset_increment, evaluate_until_onset)
            [out.update({'piece': csv_file, 'alg': algorithm}) for out in outputlist]
            complete_list.extend(outputlist)
    outdf = pd.DataFrame(complete_list)
    filename = outdir+algorithm+'.csv'
    outdf.to_csv(filename)


def evaluate_tec(original, generated):
    '''  
    given a list of original and generated events, calculate
    precision and recall based on translation equivalence.
    '''
    translation_vectors = []
    generated_vec = np.array([(float(s['onset']), int(s['pitch'])) for s in generated])
    original_list = [(float(s['onset']), int(s['pitch'])) for s in original]
    for i in original_list:
        vectors = generated_vec - i
        translation_vectors.extend([tuple(v) for v in vectors])
    grouped_vectors = dict(Counter(translation_vectors))
    max_translation = max([grouped_vectors[k] for k in grouped_vectors])
    recall = max_translation/float(len(original))
    precision = max_translation/float(len(generated))
    output = {'recall': recall, 'precision': precision}
    return output


def evaluate_list(original, generated, last_onset_prime):
    original_pitches = [int(o['pitch']) for o in original]
    generated_pitches = [int(g['pitch']) for g in generated]
    original_iois = [
        round(
            float(o['onset']) - last_onset_prime, 2
        ) for o in original
    ]
    generated_iois = [
        round(
            float(g['onset']) - last_onset_prime, 2
        ) for g in generated
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
    prec_pitch = correct_pitches_at_n / len(generated)
    prec_ioi = correct_iois_at_n / len(generated)
    prec_pairs = correct_pairs_at_n / len(generated)
    rec_pitch = correct_pitches_at_n / len(original)
    rec_ioi = correct_iois_at_n / len(original)
    rec_pairs = correct_pairs_at_n / len(original)
    output = {
        'no_predicted_events': len(original),
        'pitches_correct': correct_pitches_at_n,
        'iois_correct': correct_iois_at_n,
        'pitch_ioi_pairs_correct': correct_pairs_at_n,
        'prec_pitch': prec_pitch,
        'prec_ioi': prec_ioi,
        'prec_pairs': prec_pairs,
        'rec_pitch': rec_pitch,
        'rec_ioi': rec_ioi,
        'rec_pairs': rec_pairs
    }
    return output


def evaluate_continuation(
    original, 
    generated, 
    last_event_prime,
    evaluation_method,
    onset_increment, 
    evaluate_until_onset):
    """ Given the original and the generated continuation
    of the test item (in onset/pitch dictionaries),
    collect the following events (which can be mulitple pitches),
    and determine how many pitches / iois and pitch/ioi pairs are shared between 
    generated and original piece.
    onset_increment determines the increase of onset steps in evaluation.
    For the first ioi, the last event of the prime is also required.
    'evaluate_until_onset' determines until how many quarter notes 
    after the cut-off point we evaluate.
    Output is a list of dictionaries, 
    in which the key indicates the onsets after cut-off
    for which correct number of pitches, iois and pitch/ioi pairs are listed. 
    """
    output_list = []
    last_onset_prime = float(last_event_prime['onset'])
    max_onset = last_onset_prime + evaluate_until_onset
    no_steps = int(evaluate_until_onset / onset_increment)
    for step in range(1, no_steps+1):
        onset = last_onset_prime + step * onset_increment
        if onset <= max_onset:
            original_events = [o for o in original if float(o['onset']) <= onset]
            generated_events = [
                g for g in generated if float(g['onset']) <= onset
            ]
            if not generated_events or not original_events:
                continue
            if evaluation_method=="list":
                output = evaluate_list(original_events, generated_events, last_onset_prime)
            elif evaluation_method=="tec":
                output = evaluate_tec(original_events, generated_events)
            output.update({'onset': onset - last_onset_prime})
            output_list.append(output)           
    return output_list
