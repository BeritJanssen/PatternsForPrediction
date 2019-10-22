import re
import os.path as op

import pandas as pd
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt

import config

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
    pitch_scores = []
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
            pitch_score = evaluate_pitch_score(
                true_df,
                gen_df
            )
            pitch_score_nooctave = evaluate_pitch_score(
                true_df,
                gen_df,
                ignore_octave=True
            )
            pitch_scores.append(
                {'fn': fn,
                'Pitch': pitch_score, 
                'Modulo12Pitch': pitch_score_nooctave,
                'Model': alg}
            )
    scores_df = pd.DataFrame.from_dict(pitch_scores)
    data = scores_df.melt(
        id_vars=['fn', 'Model'], 
        value_vars=['Pitch', 'Modulo12Pitch'],
        var_name='score')
    plt.figure()
    sns.set_style("whitegrid")
    g = sns.FacetGrid(
        data,
        col='score',
        hue='Model',
        hue_order=config.MODEL_DIRS.keys()
        )
    g = g.map(
        sns.violinplot,
        'Model',
        'value',
        order=config.MODEL_DIRS.keys()
        # scale='width', bw=.1, cut=0
    )
    filename = op.join(config.OUTPUT_FOLDER, '{}_pitch_scores.png'.format(config.FILENAME_FRAGMENT))
    plt.savefig(filename, dpi=300)

    # tables
    pitch_stats = scores_df.groupby('Model').agg(
        {'Pitch':['mean', 'median', 'std']})
    rounded_pitch_score_table = pitch_stats.round(decimals=3)
    filename = op.join(config.OUTPUT_FOLDER, '{}_pitch_table'.format(config.FILENAME_FRAGMENT))
    rounded_pitch_score_table.to_html(filename + '.html')
    rounded_pitch_score_table.to_latex(filename + '.tex')
    pitch_no_octave_stats = scores_df.groupby('Model').agg(
        {'Modulo12Pitch':['mean', 'median', 'std']})
    rounded_pitch_score_table = pitch_no_octave_stats.round(decimals=3)
    filename = op.join(config.OUTPUT_FOLDER, '{}_pitch_no_octave_table'.format(config.FILENAME_FRAGMENT))
    rounded_pitch_score_table.to_html(filename + '.html')
    rounded_pitch_score_table.to_latex(filename + '.tex')