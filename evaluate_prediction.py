import os
import csv
import pandas as pd
from tqdm import tqdm
#import seaborn as sns
# import matplotlib.pyplot as plt
from glob import glob
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
    if precision + recall == 0:
        f1 = 0
    else:
        f1 = 2 * recall * precision / (
            recall + precision
        )
    output = {'rec_pairs': recall, 'prec_pairs': precision, 'f1_pairs': f1}
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
    if prec_pitch + rec_pitch == 0:
        f1_pitch = 0
    else:
        f1_pitch = 2 * rec_pitch * prec_pitch / (
            rec_pitch + prec_pitch)
    if prec_ioi + rec_ioi == 0:
        f1_ioi = 0
    else:
        f1_ioi = 2 * rec_ioi * prec_ioi / (
            rec_ioi + prec_ioi)
    if prec_pairs + rec_pairs == 0:
        f1_pairs = 0
    else:
        f1_pairs = 2 * rec_pairs * prec_pairs / (
            rec_pairs + prec_pairs
        )
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
        'rec_pairs': rec_pairs,
        'f1_pitch': f1_pitch,
        'f1_ioi': f1_ioi,
        'f1_pairs': f1_pairs
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
    # outputlist = []
    score_names = ['ioi', 'pitch', 'combo']
    scores = {name: {'precision': {}, 'recall': {}, 'f1': {}} 
              for name in score_names}
    last_onset_prime = float(last_event_prime['onset'])
    max_onset = last_onset_prime + evaluate_until_onset
    no_steps = int(evaluate_until_onset / onset_increment)
    for step in range(1, no_steps+1):
        onset = step * onset_increment
        cutoff = last_onset_prime + onset
        if cutoff <= max_onset:
            original_events = [o for o in original if float(o['onset']) <= cutoff]
            generated_events = [
                g for g in generated if float(g['onset']) <= cutoff
            ]
            if (len(generated_events)==0 and len(original_events)==0):
                scores['combo']['precision'][onset] = 1
                scores['combo']['recall'][onset] = 1
                scores['combo']['f1'][onset] = 1
                # prec_pitch = prec_ioi = prec_pairs = 1
                # rec_pitch = rec_ioi = rec_pairs = 1
                # f1_pitch = f1_ioi = f1_pairs = 1
                # correct_pitches_at_n = correct_iois_at_n = correct_pairs_at_n = None
            elif (len(original_events)==0 or len(generated_events)==0):
                scores['combo']['precision'][onset] = 0
                scores['combo']['recall'][onset] = 0
                scores['combo']['f1'][onset] = 0
                # prec_pitch = prec_ioi = prec_pairs = 0
                # rec_pitch = rec_ioi = rec_pairs = 0
                # f1_pitch = f1_ioi = f1_pairs = 0
                # correct_pitches_at_n = correct_iois_at_n = correct_pairs_at_n = None
            else:
                if evaluation_method=="list":
                    output = evaluate_list(original_events, generated_events, last_onset_prime)
                elif evaluation_method=="tec":
                    output = evaluate_tec(original_events, generated_events)
                scores['combo']['precision'][onset] = output['prec_pairs']
                scores['combo']['recall'][onset] = output['rec_pairs']
                scores['combo']['f1'][onset] = output['f1_pairs']
            
            # scores['pitch']['precision'][onset] = output['prec_pitch']
            # scores['pitch']['recall'][onset] = output['rec_pitch']
            # scores['pitch']['f1'][onset] = output['f1_pitch']
            # scores['ioi']['precision'][onset] = output['prec_ioi']
            # scores['ioi']['recall'][onset] = output['rec_ioi']
            # scores['ioi']['f1'][onset] = output['f1_ioi']
    return scores


# if __name__ == '__main__':   
#     # Change to point towards a folder containing the unzipped data
#     PATH = '/Users/janss089/Documents/MusicResearch/MIREX/MIREX2018/PPTD/monophonic/'
#     COLNAMES = ['onset', 'pitch', 'morph', 'dur', 'ch']
    
#     def get_fn(path):
#         return path.split('/')[-1].split('.')[0]

#     print('Reading csv files')    
#     part = 'prime'
#     prime = {get_fn(path): pd.read_csv(path, names=COLNAMES) 
#              for path in tqdm(glob('{}/{}_csv/*'.format(PATH, part)))}
#     part = 'cont_foil'
#     cont_foil = {get_fn(path): pd.read_csv(path, names=COLNAMES) 
#                  for path in tqdm(glob('{}/{}_csv/*'.format(PATH, part)))}
#     part = 'cont_true'
#     cont_true = {get_fn(path): pd.read_csv(path, names=COLNAMES) 
#                  for path in tqdm(glob('{}/{}_csv/*'.format(PATH, part)))}
#     fn_list = list(prime.keys())
#     fn = fn_list[0]   
#     print('Scoring compositions with MIREX2018 score (with nan handling)')
#     scores = {}
#     for fn in tqdm(fn_list):
#         scores[fn] = evaluate_continuation(cont_true[fn].to_dict('records'), cont_foil[fn].to_dict('records'), 
#                                         prime[fn].to_dict('records')[-1], "list",
#                                         0.5, 10.0)
#     print('Scoring compositions with TEC score')
#     old_scores = {}
#     for fn in tqdm(fn_list):
#         old_scores[fn] = evaluate_continuation(cont_true[fn].to_dict('records'), cont_foil[fn].to_dict('records'), 
#                                         prime[fn].to_dict('records')[-1], "tec",
#                                         0.5, 10.0)
    
#     # for score_type in ['pitch', 'ioi', 'combo']:
#     for metric in ['recall', 'precision', 'f1']:
#         data = {fn: scores[fn]['combo'][metric] for fn in fn_list}
#         df = (pd.DataFrame
#                  .from_dict(data, orient='index')
#                  .reset_index()
#                  .rename(columns={'index': 'fn'})
#                  .melt(id_vars=['fn'], var_name='t', value_name='score')
#              )
#         df['score_type'] = 'MIREX 2018'
#         data2 = {fn: old_scores[fn]['combo'][metric] for fn in fn_list}
#         df2 = (pd.DataFrame
#                  .from_dict(data2, orient='index')
#                  .reset_index()
#                  .rename(columns={'index': 'fn'})
#                  .melt(id_vars=['fn'], var_name='t', value_name='score')
#              )
#         df2['score_type'] = 'TEC'
        
#         plt.figure()
#         sns.lineplot(x='t', y='score', hue='score_type',
#                      data=pd.concat((df, df2), axis=0))
#         plt.title('pitch/onset pairs, {} metric'.format(metric))
#     #        plt.ylim([0, 1])
#         plt.show()
