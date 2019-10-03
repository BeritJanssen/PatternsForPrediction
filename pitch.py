import re

import pandas as pd
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt

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


def score_pitch(fn_list, alg_names, files_dict, cont_true):
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