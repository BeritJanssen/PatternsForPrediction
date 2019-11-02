#!/usr/bin/env python
"""This script evaluates the discriminative task: each candidate model applies
a probability to candidate continuations for a given primer. The higher the
probability given to the true continuation, and lower the probability given to
the false continuation(s), the better the score. In the 2019 competition, only
two continuations are scored, but this script is written in such a way that we
could accept an arbitrary number of false continuation scores.

The input data files are expected to be of the format:
    id,A,B,...,Z
    01234abcd,0.00092,0.001,...,0.9
    12345bcd3,0.092,0.01,...,0.7
    ...

Where id represents the identity of the exerpt being evaluated, the final
column is the true continuation score, and all other columns are false
continuation scores.

N.B. It is assumed that the rows sum to 1, with the values representing the
probability of each excerpt being the true continuation.
"""
import os.path as op

import numpy as np
import pandas as pd

import config
    

def get_scores(x, labels=None):
    """Returns the required scores: accuracy, mean negative log likelihood (the
    crossentropy), and the variance of the negative log likelihood. If labels
    is not supplied (a list of indices indicating the true label for each row),
    it is assumed the final column of each row is the true label (this is very
    specific to our particular expected input!)"""
    nr_obs = x.shape[0]
    nr_cols = x.shape[1]
    max_idx = nr_cols - 1
    if labels is None:
        labels = max_idx * np.ones(nr_obs, dtype=int)
    accuracy = np.mean(np.argmax(x, axis=-1) == labels)
    avg_prob = np.mean(x[:, labels])
    var_prob = np.var(x[:, labels])
    return nr_obs, accuracy, avg_prob, var_prob


if __name__ == '__main__':
    paths = {
        'mono': config.DISCRIM_MONO_FILES,
        'poly': config.DISCRIM_POLY_FILES
    }
    
    # Score each file
    scores = pd.DataFrame(
        columns=['model', 'data', 'nr_obs', 'accuracy', 'mean_probability',
                 'var_prob'],
        dtype=float
    )
    scores.nr_obs = scores.nr_obs.astype(int)
    scores.data = scores.data.astype(str)
    scores.model = scores.model.astype(str)
    scores.set_index(['model', 'data'], inplace=True)
    
    for data_type in list(paths.keys()):
        files = paths[data_type]
        for model_name, fn in files.items():
            df = pd.read_csv(fn)
            x = df.iloc[:, 1:].values
            if not np.allclose(np.sum(x, axis=1), np.ones(x.shape[0])):
                row_sums = x.sum(axis=1)
                x = x / row_sums[:, np.newaxis]
            scores.loc[(model_name, data_type), :] = get_scores(x)
    
    # TODO: Check files have same set of ids (warn if not)
    
    # Output table of results
    scores.round(decimals=3).to_html(op.join(config.OUTPUT_FOLDER,
                'discrim_table.html'))
    scores.round(decimals=3).to_latex(op.join(config.OUTPUT_FOLDER,
                'discrim_table.tex'))

    print(scores.round(decimals=3))