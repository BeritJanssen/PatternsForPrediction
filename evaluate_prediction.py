#!/usr/bin/env python
"""Script to evaluate all contributions for MIREX Patterns for Prediction 2019.
See README.md for configuration instructions.

References
----------
https://www.music-ir.org/mirex/wiki/2019:Patterns_for_Prediction
"""
import re
from glob import glob
from collections import Counter

import pandas as pd
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt

import config


def evaluate_cs(original, generated):
    '''Given a original and generated events, calculate precision, recall, and
    F1 of the cardinality score. It is expected that `original` and `generated`
    are pandas dataframes containing columns 'onset' and 'pitch' and that they
    have been deduplicated.

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
    '''
    translation_vectors = []
    generated_vec = generated[['onset', 'pitch']].values
    original_list = original[['onset', 'pitch']].values.tolist()
    for point in original_list:
        vectors = generated_vec - point
        translation_vectors.extend([tuple(v) for v in vectors])
    vector_counts = Counter(translation_vectors)
    most_common_vector, count = vector_counts.most_common(1)[0]
    recall = (count - 1) / float(len(original) - 1)
    precision = (count - 1) / float(len(generated) - 1)
    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = (2 * recall * precision) / (
            recall + precision
        )
    output = {'rec': recall, 'prec': precision, 'F1': f1}
    return output


def evaluate_pitch_score(original, generated, ignore_octave=False):
    '''Given a original and generated events, calculate the pitch score. It is
    expected that `original` and `generated` are pandas dataframes containing
    columns 'onset' and 'pitch' and that they have been deduplicated. The pitch
    score is the overlap of the normalised histograms of the pitches.

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
    overlap : float
        The proportion of overlap between the normalised pitch histograms
    '''
    if ignore_octave is True:
        original = original.copy()
        original['pitch'] = original['pitch'] % 12
        generated = generated.copy()
        generated['pitch'] = generated['pitch'] % 12
    orig_pitch = original.pitch.value_counts(normalize=True)
    orig_pitch.name = 'orig_pitch'
    gen_pitch = generated.pitch.value_counts(normalize=True)
    gen_pitch.name = 'gen_pitch'
    pitches = pd.concat((orig_pitch, gen_pitch), axis=1)
    overlap = 0
    for pitch, row in pitches.iterrows():
         if not row.isnull().any():
             overlap += min(row.iloc[0], row.iloc[1])
    return overlap
    

def evaluate_continuation(original, generated, last_onset_prime,
                          onset_increment, evaluate_from_onset,
                          evaluate_until_onset):
    """Given the original and the generated continuations, get the cardinality
    score at different increments through time.

    arameters
    ----------
    original : pd.DataFrame
        A dataframe containing columns 'onset' and 'pitch' representing the
        true continuation
    generated : pd.DataFrame
        A dataframe containing columns 'onset' and 'pitch' representing the
        generated continuation to be evaluated
    last_onset_prime : int
        The onset time of the last onset of the prime
    onset_increment : float
        The increment to increase onset steps by for evaluation
    evaluate_from_onset : float
        The minimum number of onsets after `last_onset_prime` to evaluate the
        continuation from
    evaluate_until_onset : float
        The maximum number of onsets after `last_onset_prime` to evaluate the
        continuation to

    Returns
    -------
    output : dict[dict[float]]
        A dictionary containing three keys: 'rec', 'prec' and 'F1', under each
        of these is another dictionary with keys representing the number of
        onsets being evaluated to.
    """
    scores = {'precision': {}, 'recall': {}, 'F1': {}}
    nr_steps = int((evaluate_until_onset - evaluate_from_onset)
                   / onset_increment)
    max_onset = evaluate_until_onset + last_onset_prime
    for step in range(nr_steps + 1):
        onset = step * onset_increment + evaluate_from_onset
        cutoff = last_onset_prime + onset
        if cutoff <= max_onset:
            # Select all rows with onset times less than or equal to cutoff
            original_events = original[original['onset'] <= cutoff]
            generated_events = generated[generated['onset'] <= cutoff]
            if (len(original_events) <= 1 or len(generated_events) <= 1):
                scores['precision'][onset] = None
                scores['recall'][onset] = None
                scores['F1'][onset] = None
            else:
                output = evaluate_cs(original_events, generated_events)
                scores['precision'][onset] = output['prec']
                scores['recall'][onset] = output['rec']
                scores['F1'][onset] = output['F1']
    return scores


def dedup_and_preproc(df):
    """In order that CS works correctly, we need to ensure there are no
    duplicate points in (onset, pitch) space. Given that score do not use
    any other data than onset and pitch, we are safe to drop other columns
    """
    df = df[['onset', 'pitch']].drop_duplicates()
    return df


if __name__ == '__main__':
    PATH = config.DATASET_PATH
    # CSV column keys in dataset
    COLNAMES = ['onset', 'pitch', 'morph', 'dur', 'ch']

    def get_fn(path):
        """Get the filename of the csv file to evaluate"""
        return path.split('/')[-1].split('.')[0]

    print('Reading PPTD csv files')
    prime = {get_fn(path): pd.read_csv(path, names=COLNAMES)
             for path in tqdm(glob(f'{PATH}/prime_csv/*'))}
    cont_true = {get_fn(path): pd.read_csv(path, names=COLNAMES)
                 for path in tqdm(glob(f'{PATH}/cont_true_csv/*'))}
    # preprocessing to remove duplicates
    cont_true = {fn: dedup_and_preproc(df) for fn, df in cont_true.items()}
    fn_list = list(prime.keys())

    files_dict = {}
    alg_names = config.MODEL_DIRS.keys()
    for alg in alg_names:
        print(f'Reading {alg} output files')
        alg_cont = {
            get_fn(path): pd.read_csv(path, names=config.MODEL_KEYS[alg])
            for path in tqdm(glob(f'{config.MODEL_DIRS[alg]}/*.csv'))
        }
        # preprocessing to remove duplicates
        alg_cont = {fn: dedup_and_preproc(df) for fn, df in alg_cont.items()}
        files_dict[alg] = alg_cont
        
    
    card_scores = {alg: {} for alg in alg_names}

    for alg in alg_names:
        print(f'Scoring {alg} with cardinality score')
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
        metric = 'cardinality'
        for key in card_scores.keys():
            data = {fn: card_scores[key][fn][measure] for fn in fn_list}
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


    pitch_scores = {alg: {} for alg in alg_names}
    pitch_scores_nooctave = {alg: {} for alg in alg_names}
    for alg in alg_names:
        print(f'Scoring {alg} with pitch score')
        for fn in tqdm(fn_list):
            # the generated file name may have additions to original file name
            generated_fn = next(
                (alg_fn for alg_fn in files_dict[alg].keys()
                 if re.search(fn, alg_fn)),
                None
            )
            true_df = cont_true[fn]
            gen_df = files_dict[alg][generated_fn]
            pitch_scores[alg][fn] = evaluate_pitch_score(
                true_df,
                gen_df
            )
            pitch_scores_nooctave[alg][fn] = evaluate_pitch_score(
                true_df,
                gen_df,
                ignore_octave=True
            )
            
    metric = 'pitch'
    df_list = []
    pitch_score_table = pd.DataFrame(columns=['mean', 'median', 'sd'],
                                     dtype=float)
    pitch_score_table.index.name = 'alg'
    for key in pitch_scores.keys():
        data = {fn: pitch_scores[key][fn] for fn in fn_list}
        df = (
            pd.DataFrame
                .from_dict(data, orient='index')
                .reset_index()
                .rename(columns={'index': 'fn', 0: 'pitch_score'})
        )
        df['model'] = key
        df_list.append(df)
        pitch_score_table.loc[key, :] = [df.pitch_score.mean(),
                                           df.pitch_score.median(),
                                           df.pitch_score.std()]
    df = pd.concat(df_list, axis=0)
    plt.figure()
    sns.set_style("whitegrid")
    sns.violinplot(x='model', y='pitch_score', data=df, ax=plt.gca(),
                   scale='width', bw=.1, cut=0)
    plt.title(f'Comparison of {metric} score')
    filename = f"{metric}_score.png"
    plt.savefig(filename, dpi=300)
    rounded_pitch_score_table = pitch_score_table.round(decimals=3)
    print(rounded_pitch_score_table)
    rounded_pitch_score_table.to_html(f'{metric}_score_table.html')
    rounded_pitch_score_table.to_latex(f'{metric}_score_table.tex')
    
    
    metric = 'pitch_no_octave'
    df_list = []
    pitch_score_table = pd.DataFrame(columns=['mean', 'median', 'sd'],
                                     dtype=float)
    pitch_score_table.index.name = 'alg'
    for key in pitch_scores_nooctave.keys():
        data = {fn: pitch_scores_nooctave[key][fn] for fn in fn_list}
        df = (
            pd.DataFrame
                .from_dict(data, orient='index')
                .reset_index()
                .rename(columns={'index': 'fn', 0: 'pitch_score'})
        )
        df['model'] = key
        df_list.append(df)
        pitch_score_table.loc[key, :] = [df.pitch_score.mean(),
                                         df.pitch_score.median(),
                                         df.pitch_score.std()]
    df = pd.concat(df_list, axis=0)
    plt.figure()
    sns.set_style("whitegrid")
    sns.violinplot(x='model', y='pitch_score', data=df, ax=plt.gca(),
                   scale='width', bw=.1, cut=0)
    plt.title(f'Comparison of {metric} score')
    filename = f"{metric}_score.png"
    plt.savefig(filename, dpi=300)
    rounded_pitch_score_table = pitch_score_table.round(decimals=3)
    print(rounded_pitch_score_table)
    rounded_pitch_score_table.to_html(f'{metric}_score_table.html')
    rounded_pitch_score_table.to_latex(f'{metric}_score_table.tex')
