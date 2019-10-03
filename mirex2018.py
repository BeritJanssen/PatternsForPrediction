import re

import pandas as pd
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt

import config

def evaluate_sets(
    original, 
    generated, 
    evaluate_from_onset, 
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

    Parameters
    ----------
    original : pd.DataFrame
        A dataframe containing columns 'onset' and 'pitch' representing the
        true continuation
    generated : pd.DataFrame
        A dataframe containing columns 'onset' and 'pitch' representing the
        generated continuation to be evaluated

    Returns
    -------
    output : dict[float]
        A dictionary containing three keys: 'rec', 'prec' and 'F1', the recall
        precision and the F1 of the cardinality score.
    """
    scores = {'precision': {}, 'recall': {}, 'F1': {}}
    nr_steps = int((evaluate_until_onset - evaluate_from_onset)
                   / onset_increment)
    original_onsets = sorted(list(set(original[['onset']].values())))
    generated_onsets = sorted(list(set(generated[['onset']].values())))
    max_onset = evaluate_from_onset + evaluate_until_onset
    for step in range(1, nr_steps+1):
        cutoff = evaluate_from_onset + step * onset_increment
        if cutoff <= max_onset:
            original_events = original[['onset'] <= cutoff]
            generated_events = generated[['onset'] <= cutoff]
            if not generated_events or not original_events:
                continue
            original_pitches = [int(o['pitch']) for o in original_events]
            generated_pitches = [int(g['pitch']) for g in generated_events]
            original_iois = [
                round(
                    float(o['onset']) - last_onset_prime, 2
                ) for o in original_events
            ]
            generated_iois = [
                round(
                    float(g['onset']) - last_onset_prime, 2
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
            prec_pitch = correct_pitches_at_n / len(generated_events)
            prec_ioi = correct_iois_at_n / len(generated_events)
            prec_pairs = correct_pairs_at_n / len(generated_events)
            rec_pitch = correct_pitches_at_n / len(original_events)
            rec_ioi = correct_iois_at_n / len(original_events)
            rec_pairs = correct_pairs_at_n / len(original_events)
            outputlist.append({
                'onset': onset - last_onset_prime,
                'pitches_correct': correct_pitches_at_n,
                'iois_correct': correct_iois_at_n,
                'pitch_ioi_pairs_correct': correct_pairs_at_n,
                'no_predicted_events': len(original_events),
                'prec_pitch': prec_pitch,
                'prec_ioi': prec_ioi,
                'prec_pairs': prec_pairs,
                'rec_pitch': rec_pitch,
                'rec_ioi': rec_ioi,
                'rec_pairs': rec_pairs
            })
    return outputlist


    def score_sets(fn_list, alg_names, files_dict, cont_true, prime):
    set_scores = {alg: {} for alg in alg_names}
    for alg in alg_names:
        print(f'Scoring {alg} with set score')
        for fn in tqdm(fn_list):
            # the generated file name may have additions to original file name
            generated_fn = next(
                (alg_fn for alg_fn in files_dict[alg].keys()
                 if re.search(fn, alg_fn)),
                None
            )
            true_df = cont_true[fn]
            gen_df = files_dict[alg][generated_fn]
            prime_final_onset = prime[fn].iloc[-1]['onset']
            card_scores[alg][fn] = evaluate_continuation(
                true_df,
                gen_df,
                prime_final_onset,
                0.5, 2.0, 10.0
            )
    
    df_list = []
    for measure in ['recall', 'precision', 'F1']:
        metric = 'set'
        for key in set_scores.keys():
            data = {fn: set_scores[key][fn][measure] for fn in fn_list}
            df = (pd.DataFrame
                    .from_dict(data, orient='index')
                    .reset_index()
                    .rename(columns={'index': 'fn'})
                    .melt(id_vars=['fn'], var_name='t',
                          value_name=f'{metric} score')
            )
            df['model'] = key
            df_list.append(df)
        plt.figure()
        sns.set_style("whitegrid")
        g = sns.lineplot(
            x='t',
            y=f'{metric} score',
            hue='model',
            hue_order=config.MODEL_DIRS.keys(),
            style='model',
            style_order=config.MODEL_DIRS.keys(),
            markers=['o', 'v', 's'],
            data=pd.concat((df_list), axis=0)
        )
        g.set(xlabel='Onset', ylabel=str.title(measure))
        plt.title(f'Comparison by {measure} of {metric} score')
        filename = f"{metric}_score__{measure}.png"
        plt.savefig(filename, dpi=300)