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
"""
import numpy as np
import pandas as pd

import config



def softmax(x, axis=-1):
    """Returns the softmax for each row of the input x. For numerical
    stability, we subtract the maximum value from each row first before getting
    the exponents.
    """
    exp = np.exp(x - np.max(x, axis=axis, keepdims=True))
    return exp / np.sum(exp, axis=axis, keepdims=True)


def negloglike(x, labels):
    """Returns the negative log likelihood from each row of x (unnormalized
    probabilities - we apply a softmax to each row first).
    """
    probs = softmax(x)
    return -np.log(probs[:, labels])  # select only the prob of true lab
    

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
    nll = negloglike(x, labels)
    crossent = np.mean(nll)
    nll_var = np.var(nll)
    return nr_obs, accuracy, crossent, nll_var


if __name__ == '__main__':
    paths = {
        'mono': config.DISCRIM_MONO_FILES,
        'poly': config.DISCRIM_POLY_FILES
    }
    
    # Score each file
    scores = pd.DataFrame(
        columns=['model', 'data', 'nr_obs', 'accuracy', 'crossentropy',
                 'nll_var'],
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
            scores.loc[(model_name, data_type), :] = get_scores(x)
    
    # TODO: Check files have same set of ids (warn if not)
    
    # TODO: Output table of results
    scores.round(decimals=3).to_html('./discrim_table.html')
    scores.round(decimals=3).to_latex('./discrim_table.tex')
