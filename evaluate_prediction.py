import os
import csv
import re
import click
import pandas as pd
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt
from glob import glob
import numpy as np
from collections import Counter


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
    recall = (max_translation - 1) / float(len(original) -1)
    precision = (max_translation - 1) / float(len(generated) -1)
    if precision + recall == 0:
        f1 = 0
    else:
        f1 = 2 * recall * precision / (
            recall + precision
        )
    output = {'rec': recall, 'prec': precision, 'f1': f1}
    return output


def evaluate_continuation(
    original, 
    generated,
    last_onset_prime,
    onset_increment,
    evaluate_from_onset,
    evaluate_until_onset):
    """ Given the original and the generated continuation
    of the test item (in onset/pitch dictionaries),
    collect the following events and get tec score.
    'onset_increment' determines the increase of onset steps in evaluation.
    For the first ioi, the last event of the prime is also required.
    'evaluate_until_onset' determines until how many quarter notes 
    after the cut-off point we evaluate.
    """
    # outputlist = []
    scores = {'precision': {}, 'recall': {}, 'f1': {}}
    no_steps = int((evaluate_until_onset - evaluate_from_onset) / onset_increment)
    max_onset = evaluate_until_onset + last_onset_prime
    for step in range(no_steps+1):
        onset = step * onset_increment + evaluate_from_onset
        cutoff = last_onset_prime + onset
        if cutoff <= max_onset:
            original_events = [o for o in original if float(o['onset']) <= cutoff]
            generated_events = [
                g for g in generated if float(g['onset']) <= cutoff
            ]
            if (len(original_events)<=1 or len(generated_events)<=1):
                scores['precision'][onset] = None
                scores['recall'][onset] = None
                scores['f1'][onset] = None
            else:
                output = evaluate_tec(original_events, generated_events)
                scores['precision'][onset] = output['prec']
                scores['recall'][onset] = output['rec']
                scores['f1'][onset] = output['f1']
    return scores


if __name__ == '__main__':  
    # Change to point towards a folder containing the unzipped data
    PATH = '/Users/janss089/Documents/MusicResearch/MIREX/MIREX2018/PPTD/monophonic/'
    COLNAMES = ['onset', 'pitch', 'morph', 'dur', 'ch']
    compare_dirs = {
        "FC1": "/Users/janss089/Documents/MusicResearch/MIREX/MIREX2018/Results/FC1/output_mono/1/cont_pred_csv",
        "EN1": "/Users/janss089/Documents/MusicResearch/MIREX/MIREX2018/Results/EN1/mono",
        "MM1": "/Users/janss089/Documents/MusicResearch/MIREX/MIREX2018/PPTD/monophonic/cont_foil_csv"
    }
    compare_keys = {
        "FC1": ['onset', 'pitch', 'ioi'],
        "EN1": COLNAMES,
        "MM1": COLNAMES
    }
    
    def get_fn(path):
        return path.split('/')[-1].split('.')[0]

    print('Reading PPTD csv files')    
    part = 'prime'
    prime = {get_fn(path): pd.read_csv(path, names=COLNAMES) 
             for path in tqdm(glob('{}/{}_csv/*'.format(PATH, part)))}
    part = 'cont_true'
    cont_true = {get_fn(path): pd.read_csv(path, names=COLNAMES) 
                 for path in tqdm(glob('{}/{}_csv/*'.format(PATH, part)))}
    fn_list = list(prime.keys())
    fn = fn_list[0]
    files_dict = {}
    for alg in compare_dirs.keys():
        print('Reading {} output files'.format(alg))
        files_dict[alg] = {get_fn(path): pd.read_csv(path, names=compare_keys[alg]) 
                 for path in tqdm(glob('{}/*.csv'.format(compare_dirs[alg])))}
    scores = {key: {} for key in files_dict.keys()}
    for alg in files_dict.keys():
        print('Scoring {} results with TEC score'.format(alg))
        for fn in tqdm(fn_list):
            # the generated file name may have additions to original file name
            generated_fn = next((alg_fn for alg_fn in files_dict[alg].keys() if re.search(fn, alg_fn)), None)
            scores[alg][fn] = evaluate_continuation(cont_true[fn].to_dict('records'), files_dict[alg][generated_fn].to_dict('records'), 
                                        prime[fn].to_dict('records')[-1]['onset'],
                                        0.5, 2.0, 10.0)                                        
    df_list = []
    for metric in ['recall', 'precision', 'f1']:
        for key in scores.keys():
            data = {fn: scores[key][fn][metric] for fn in fn_list}
            df = (pd.DataFrame
                 .from_dict(data, orient='index')
                 .reset_index()
                 .rename(columns={'index': 'fn'})
                 .melt(id_vars=['fn'], var_name='t', value_name='score')
             )
            df['model'] = key
            df_list.append(df)
        
        plt.figure()
        g = sns.lineplot(x='t', y='score', hue='model',
                     data=pd.concat((df_list), axis=0))
        g.set(xlabel='Onset', ylabel=str.upper(metric))
        plt.title('Comparison of models on {} metric'.format(metric))
    #        plt.ylim([0, 1])
        plt.show()
